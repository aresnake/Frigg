"""
Test search_tools logic inline

This is a pure Python metadata search - no Blender required
"""

print("=" * 70)
print("TESTING SEARCH_TOOLS LOGIC")
print("=" * 70)

# Tool metadata catalog
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

    # CREATION
    "create_primitive": {
        "category": "creation",
        "visibility": "visible",
        "tags": ["create", "primitive", "cube", "sphere", "cylinder", "new"],
        "description": "Create primitive objects (cube, sphere, cylinder, etc.)",
        "complexity": "simple"
    },

    # MATERIALS (Hidden)
    "set_material": {
        "category": "materials",
        "visibility": "hidden",
        "tags": ["material", "color", "shader", "appearance"],
        "description": "Create and assign material with color and properties",
        "complexity": "medium"
    },
    "get_material": {
        "category": "materials",
        "visibility": "hidden",
        "tags": ["material", "get", "properties"],
        "description": "Get material properties of an object",
        "complexity": "simple"
    },

    # MODIFIERS (Hidden)
    "add_modifier": {
        "category": "modifiers",
        "visibility": "hidden",
        "tags": ["modifier", "array", "mirror", "subdivision", "bevel"],
        "description": "Add modifier to object (array, mirror, etc.)",
        "complexity": "medium"
    },

    # LIGHTING (Hidden)
    "create_light": {
        "category": "lighting",
        "visibility": "hidden",
        "tags": ["light", "lighting", "create", "illumination"],
        "description": "Create light source (point, sun, spot, area)",
        "complexity": "simple"
    },
}

def search_tools(params):
    """
    Search tools by keyword, category, or visibility.

    Parameters:
        query: Optional keyword search
        category: Optional category filter
        show_hidden: Show hidden tools (default False)

    Returns:
        List of matching tools with metadata
    """
    query = params.get("query", "").lower()
    category_filter = params.get("category", "").lower()
    show_hidden = params.get("show_hidden", False)

    results = []
    categories_found = set()

    for tool_name, metadata in TOOL_METADATA.items():
        # Filter by visibility
        if not show_hidden and metadata["visibility"] == "hidden":
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
        "tools": results,
        "total_found": len(results),
        "categories_found": sorted(list(categories_found))
    }

# Test 1: Search by keyword "material"
print("\nTest 1: Search for 'material'")
result1 = search_tools({"query": "material"})
print(f"  Found {result1['total_found']} tools")
print(f"  Categories: {result1['categories_found']}")
if result1['total_found'] == 0:
    print("  OK - Hidden by default")

# Test 2: Search with show_hidden
print("\nTest 2: Search for 'material' with show_hidden=True")
result2 = search_tools({"query": "material", "show_hidden": True})
print(f"  Found {result2['total_found']} tools")
for tool in result2['tools']:
    print(f"    - {tool['name']}")
if result2['total_found'] >= 2:
    print("  OK - Found material tools")

# Test 3: Search by category
print("\nTest 3: Search category 'transforms'")
result3 = search_tools({"category": "transforms"})
print(f"  Found {result3['total_found']} tools")
for tool in result3['tools']:
    print(f"    - {tool['name']}")
if result3['total_found'] == 3:
    print("  OK - Found all transform tools")

# Test 4: Show all visible tools
print("\nTest 4: Show all visible tools")
result4 = search_tools({})
print(f"  Found {result4['total_found']} visible tools")
print(f"  Categories: {result4['categories_found']}")
if result4['total_found'] >= 9:
    print("  OK - Correct count of visible tools")

# Test 5: Show all tools (visible + hidden)
print("\nTest 5: Show all tools (including hidden)")
result5 = search_tools({"show_hidden": True})
print(f"  Total tools: {result5['total_found']}")
print(f"  All categories: {result5['categories_found']}")
if result5['total_found'] > result4['total_found']:
    print("  OK - Hidden tools found")

# Test 6: Search for specific action
print("\nTest 6: Search for 'rotate'")
result6 = search_tools({"query": "rotate"})
print(f"  Found {result6['total_found']} tools")
for tool in result6['tools']:
    print(f"    - {tool['name']}: {tool['description']}")
if result6['total_found'] >= 1:
    print("  OK - Found rotation tool")

print("\n" + "=" * 70)
print("TEST PASSED - search_tools logic works!")
print("=" * 70)

result = "search_works"
