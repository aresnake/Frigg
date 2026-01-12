from typing import Any, Dict

from frigg_mcp.tools.core_tools import ok_result


TOOL_METADATA = {
    # CORE
    "scene_info": {
        "category": "core",
        "visibility": "visible",
        "tags": ["scene", "info", "basics"],
        "description": "Get basic scene information",
        "complexity": "simple",
    },
    "list_objects": {
        "category": "core",
        "visibility": "visible",
        "tags": ["list", "objects", "scene"],
        "description": "List all objects in scene",
        "complexity": "simple",
    },
    # TRANSFORMS
    "set_object_location": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["move", "position", "location", "transform"],
        "description": "Set object location/position",
        "complexity": "simple",
    },
    "set_object_rotation": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["rotate", "rotation", "angle", "transform"],
        "description": "Set object rotation",
        "complexity": "simple",
    },
    "set_object_scale": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["scale", "size", "resize", "transform"],
        "description": "Set object scale",
        "complexity": "simple",
    },
    "get_object_transform": {
        "category": "transforms",
        "visibility": "visible",
        "tags": ["get", "read", "transform", "position"],
        "description": "Get object transform (location/rotation/scale)",
        "complexity": "simple",
    },
    # VISION
    "viewport_snapshot": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["view", "screenshot", "image", "render", "vision"],
        "description": "Capture viewport as image",
        "complexity": "simple",
    },
    "get_bounding_box": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["measure", "dimensions", "size", "bounds"],
        "description": "Get object bounding box and dimensions",
        "complexity": "simple",
    },
    "get_spatial_relationships": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["spatial", "position", "relationship", "above", "below"],
        "description": "Determine spatial relationships between objects",
        "complexity": "simple",
    },
    # CREATION (will be added as implemented)
    "create_primitive": {
        "category": "creation",
        "visibility": "visible",
        "tags": ["create", "primitive", "cube", "sphere", "cylinder", "new"],
        "description": "Create primitive objects (cube, sphere, cylinder, etc.)",
        "complexity": "simple",
    },
    "duplicate_object": {
        "category": "creation",
        "visibility": "visible",
        "tags": ["duplicate", "copy"],
        "description": "Duplicate object",
        "complexity": "simple",
    },
    "delete_object": {
        "category": "operations",
        "visibility": "visible",
        "tags": ["delete", "remove"],
        "description": "Delete object",
        "complexity": "simple",
    },
    "rename_object": {
        "category": "operations",
        "visibility": "visible",
        "tags": ["rename", "name"],
        "description": "Rename object",
        "complexity": "simple",
    },
    "set_material": {
        "category": "materials",
        "visibility": "visible",
        "tags": ["material", "color", "shader"],
        "description": "Set material",
        "complexity": "simple",
    },
    "set_parent": {
        "category": "hierarchy",
        "visibility": "visible",
        "tags": ["parent", "hierarchy"],
        "description": "Parent objects",
        "complexity": "simple",
    },
    "set_smooth_shading": {
        "category": "materials",
        "visibility": "visible",
        "tags": ["smooth", "shading"],
        "description": "Smooth shading",
        "complexity": "simple",
    },
}


def handle_search_tools(arguments: Dict[str, Any]) -> Dict[str, Any]:
    args = arguments or {}
    query = args.get("query", "").lower()
    category_filter = args.get("category", "").lower()
    show_hidden = args.get("show_hidden", False)

    results = []
    categories_found = set()

    for tool_name, metadata in TOOL_METADATA.items():
        if not show_hidden and metadata["visibility"] != "visible":
            continue
        if category_filter and metadata["category"] != category_filter:
            continue
        if query:
            searchable = (
                tool_name.lower()
                + " "
                + " ".join(metadata["tags"])
                + " "
                + metadata["description"].lower()
            )
            if query not in searchable:
                continue

        results.append(
            {
                "name": f"frigg.blender.{tool_name}",
                "category": metadata["category"],
                "description": metadata["description"],
                "visibility": metadata["visibility"],
                "tags": metadata["tags"],
                "complexity": metadata["complexity"],
            }
        )
        categories_found.add(metadata["category"])

    return ok_result(
        {
            "tools": results,
            "total_found": len(results),
            "categories_found": sorted(list(categories_found)),
        }
    )
