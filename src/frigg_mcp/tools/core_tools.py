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
    # SPACE MARINE MODELING TOOLS (v0.5)
    {
        "name": "frigg.blender.add_modifier",
        "description": "Add a modifier to an object (Mirror, Subdivision, Boolean, Array, Solidify). Essential for armor symmetry and details.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Object to modify."},
                "modifier_type": {
                    "type": "string",
                    "enum": ["MIRROR", "SUBSURF", "BOOLEAN", "ARRAY", "SOLIDIFY"],
                    "description": "Modifier type.",
                },
                "name": {"type": "string", "description": "Optional custom modifier name."},
                # Mirror specific
                "axis_x": {"type": "boolean", "description": "Mirror on X axis (default: True).", "default": True},
                "axis_y": {"type": "boolean", "description": "Mirror on Y axis (default: False).", "default": False},
                "axis_z": {"type": "boolean", "description": "Mirror on Z axis (default: False).", "default": False},
                "use_bisect_axis": {
                    "type": "array",
                    "items": {"type": "boolean"},
                    "minItems": 3,
                    "maxItems": 3,
                    "description": "Bisect geometry on axes [x, y, z].",
                },
                # Subdivision specific
                "levels": {"type": "integer", "minimum": 0, "description": "Viewport subdivision levels (default: 2)."},
                "render_levels": {"type": "integer", "minimum": 0, "description": "Render subdivision levels (default: 2)."},
                # Boolean specific
                "operation": {
                    "type": "string",
                    "enum": ["DIFFERENCE", "UNION", "INTERSECT"],
                    "description": "Boolean operation type.",
                },
                "target_object": {"type": "string", "description": "Object to use for boolean operation."},
                # Array specific
                "count": {"type": "integer", "minimum": 1, "description": "Number of array copies (default: 2)."},
                "offset_x": {"type": "number", "description": "X offset (default: 2.0)."},
                "offset_y": {"type": "number", "description": "Y offset (default: 0.0)."},
                "offset_z": {"type": "number", "description": "Z offset (default: 0.0)."},
                # Solidify specific
                "thickness": {"type": "number", "description": "Solidify thickness (default: 0.1)."},
                "offset": {"type": "number", "description": "Solidify offset factor (default: 0.0)."},
            },
            "required": ["object_name", "modifier_type"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.apply_modifier",
        "description": "Apply (bake) a modifier to make it permanent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Object with modifier."},
                "modifier_name": {"type": "string", "description": "Name of modifier to apply."},
            },
            "required": ["object_name", "modifier_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.list_modifiers",
        "description": "List all modifiers on an object with their properties.",
        "inputSchema": {
            "type": "object",
            "properties": {"object_name": {"type": "string", "description": "Object to query."}},
            "required": ["object_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.boolean_operation",
        "description": "Perform boolean operation between two objects (Union/Difference/Intersect). Essential for armor cuts and details.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "base_object": {"type": "string", "description": "Base object to modify."},
                "target_object": {"type": "string", "description": "Object to use for boolean."},
                "operation": {
                    "type": "string",
                    "enum": ["DIFFERENCE", "UNION", "INTERSECT"],
                    "description": "Boolean operation (default: DIFFERENCE).",
                    "default": "DIFFERENCE",
                },
                "apply": {"type": "boolean", "description": "Apply immediately (default: False).", "default": False},
                "hide_target": {"type": "boolean", "description": "Hide target after operation (default: True).", "default": True},
            },
            "required": ["base_object", "target_object"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.create_material",
        "description": "Create a new PBR material with Principled BSDF shader.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Material name."},
                "base_color": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0, "maximum": 1},
                    "minItems": 4,
                    "maxItems": 4,
                    "description": "Base color [r, g, b, a] (default: [0.8, 0.8, 0.8, 1.0]).",
                },
                "metallic": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Metallic value 0-1 (default: 0.0).",
                },
                "roughness": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "Roughness value 0-1 (default: 0.5).",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.assign_material",
        "description": "Assign a material to an object.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Object to assign material to."},
                "material_name": {"type": "string", "description": "Material to assign."},
                "slot_index": {"type": "integer", "minimum": 0, "description": "Material slot index (default: 0).", "default": 0},
            },
            "required": ["object_name", "material_name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.create_collection",
        "description": "Create a new collection for organizing objects.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Collection name."},
                "parent_collection": {"type": "string", "description": "Optional parent collection name."},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "frigg.blender.move_to_collection",
        "description": "Move an object to a specific collection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "object_name": {"type": "string", "description": "Object to move."},
                "collection_name": {"type": "string", "description": "Target collection."},
                "unlink_from_current": {
                    "type": "boolean",
                    "description": "Unlink from current collections (default: True).",
                    "default": True,
                },
            },
            "required": ["object_name", "collection_name"],
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

    # SPACE MARINE MODELING TOOLS
    if name == "frigg.blender.add_modifier":
        payload = {
            "object_name": args.get("object_name"),
            "modifier_type": args.get("modifier_type"),
        }
        if args.get("name") is not None:
            payload["name"] = args.get("name")
        # Mirror specific
        if args.get("axis_x") is not None:
            payload["axis_x"] = args.get("axis_x")
        if args.get("axis_y") is not None:
            payload["axis_y"] = args.get("axis_y")
        if args.get("axis_z") is not None:
            payload["axis_z"] = args.get("axis_z")
        if args.get("use_bisect_axis") is not None:
            payload["use_bisect_axis"] = args.get("use_bisect_axis")
        # Subdivision specific
        if args.get("levels") is not None:
            payload["levels"] = args.get("levels")
        if args.get("render_levels") is not None:
            payload["render_levels"] = args.get("render_levels")
        # Boolean specific
        if args.get("operation") is not None:
            payload["operation"] = args.get("operation")
        if args.get("target_object") is not None:
            payload["target_object"] = args.get("target_object")
        # Array specific
        if args.get("count") is not None:
            payload["count"] = args.get("count")
        if args.get("offset_x") is not None:
            payload["offset_x"] = args.get("offset_x")
        if args.get("offset_y") is not None:
            payload["offset_y"] = args.get("offset_y")
        if args.get("offset_z") is not None:
            payload["offset_z"] = args.get("offset_z")
        # Solidify specific
        if args.get("thickness") is not None:
            payload["thickness"] = args.get("thickness")
        if args.get("offset") is not None:
            payload["offset"] = args.get("offset")
        return _bridge_call(call_bridge, "add_modifier", payload)

    if name == "frigg.blender.apply_modifier":
        return _bridge_call(call_bridge, "apply_modifier", {
            "object_name": args.get("object_name"),
            "modifier_name": args.get("modifier_name"),
        })

    if name == "frigg.blender.list_modifiers":
        return _bridge_call(call_bridge, "list_modifiers", {"object_name": args.get("object_name")})

    if name == "frigg.blender.boolean_operation":
        payload = {
            "base_object": args.get("base_object"),
            "target_object": args.get("target_object"),
            "operation": args.get("operation", "DIFFERENCE"),
            "apply": args.get("apply", False),
            "hide_target": args.get("hide_target", True),
        }
        return _bridge_call(call_bridge, "boolean_operation", payload)

    if name == "frigg.blender.create_material":
        payload = {"name": args.get("name")}
        if args.get("base_color") is not None:
            payload["base_color"] = args.get("base_color")
        if args.get("metallic") is not None:
            payload["metallic"] = args.get("metallic")
        if args.get("roughness") is not None:
            payload["roughness"] = args.get("roughness")
        return _bridge_call(call_bridge, "create_material", payload)

    if name == "frigg.blender.assign_material":
        return _bridge_call(call_bridge, "assign_material", {
            "object_name": args.get("object_name"),
            "material_name": args.get("material_name"),
            "slot_index": args.get("slot_index", 0),
        })

    if name == "frigg.blender.create_collection":
        payload = {"name": args.get("name")}
        if args.get("parent_collection") is not None:
            payload["parent_collection"] = args.get("parent_collection")
        return _bridge_call(call_bridge, "create_collection", payload)

    if name == "frigg.blender.move_to_collection":
        return _bridge_call(call_bridge, "move_to_collection", {
            "object_name": args.get("object_name"),
            "collection_name": args.get("collection_name"),
            "unlink_from_current": args.get("unlink_from_current", True),
        })

    return error_result("unknown_tool", f"Unknown core tool: {name}")
