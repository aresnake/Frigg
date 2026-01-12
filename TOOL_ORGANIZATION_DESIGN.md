# Tool Organization & Discovery System

**Version:** v0.11
**Date:** 2026-01-12

---

## 🎯 PROBLEM

- MCP has 30 tool limit for visibility
- We need 50+ tools eventually (modeling, materials, animation, etc.)
- Without organization, tools become hard to discover
- Current flat list doesn't scale

---

## ✅ SOLUTION: Hybrid Categorization + Search

### Core Principles

1. **Keep commonly-used tools visible** (20 tools)
2. **Hide advanced/rare tools** (unlimited, discoverable via search)
3. **Add metadata for categorization** (without changing tool names)
4. **Provide search/discovery tool** (1 tool unlocks all others)

---

## 📋 TOOL CATEGORIES

### Category: `core` (Always Visible)
- frigg.ping
- frigg.blender.bridge_ping
- frigg.blender.scene_info
- frigg.blender.list_objects

### Category: `transforms` (Always Visible)
- get_object_transform
- set_object_location
- set_object_rotation
- set_object_scale

### Category: `vision` (Always Visible)
- viewport_snapshot
- get_bounding_box
- get_spatial_relationships

### Category: `creation` (Visible)
- create_primitive ← NEW
- duplicate_object ← TODO
- delete_object ← TODO

### Category: `materials` (Hidden - Discoverable)
- set_material
- get_material
- create_material
- assign_material

### Category: `modifiers` (Hidden - Discoverable)
- add_modifier
- remove_modifier
- apply_modifier

### Category: `animation` (Hidden - Discoverable)
- keyframe_insert
- keyframe_delete
- set_frame
- bake_animation

### Category: `mesh_editing` (Hidden - Advanced)
- edit_mesh
- extrude_faces
- subdivide_mesh
- merge_vertices

### Category: `lighting` (Hidden - Discoverable)
- create_light
- set_light_properties
- set_light_color

### Category: `camera` (Hidden - Discoverable)
- create_camera
- set_camera_properties
- look_at

---

## 🔍 SEARCH TOOL

### Tool: `frigg.blender.search_tools`

**Purpose:** Discover tools by category, keyword, or capability

**Parameters:**
```python
{
    "query": str,         # Optional: keyword search
    "category": str,      # Optional: filter by category
    "show_hidden": bool   # Default false
}
```

**Returns:**
```python
{
    "tools": [
        {
            "name": "frigg.blender.set_material",
            "category": "materials",
            "description": "Create and assign material to object",
            "visibility": "hidden",
            "tags": ["material", "color", "shader"],
            "example": {
                "object_name": "Cube",
                "color": [1, 0, 0, 1],
                "metallic": 0.5
            }
        }
    ],
    "total_found": 5,
    "categories_found": ["materials", "creation"]
}
```

**Examples:**
```python
# Search by keyword
search_tools(query="material")  # Returns all material-related tools

# Search by category
search_tools(category="creation")  # Returns all creation tools

# Show all hidden tools
search_tools(show_hidden=True)  # Returns complete tool catalog

# Combined
search_tools(query="light", category="lighting")
```

---

## 📊 METADATA STRUCTURE

Each tool gets metadata in the bridge:

```python
TOOL_METADATA = {
    "set_material": {
        "category": "materials",
        "visibility": "hidden",  # or "visible"
        "tags": ["material", "color", "shader", "appearance"],
        "complexity": "medium",  # simple, medium, advanced
        "example": {...}
    },
    "viewport_snapshot": {
        "category": "vision",
        "visibility": "visible",
        "tags": ["vision", "screenshot", "view", "render"],
        "complexity": "simple",
        "example": {...}
    }
}
```

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Add search_tools (CURRENT)
1. Create `search_tools` function in bridge
2. Add TOOL_METADATA dict with categories/tags
3. Implement search logic (keyword, category, visibility)
4. Add to MCP as visible tool
5. Test search functionality

### Phase 2: Hide advanced tools
1. Add `_hidden` suffix to tool names in MCP (or use env var)
2. Keep 20 most common tools visible
3. Document how to discover hidden tools

### Phase 3: Add metadata for all tools
1. Tag all existing tools
2. Write good examples for each
3. Document categories

---

## 📈 VISIBILITY STRATEGY

### Always Visible (20 tools)
1. Core utilities (4)
2. Transforms (4)
3. Vision (3)
4. Creation (3)
5. Essential operations (3)
6. Search tool (1)
7. Buffer (2)

### Hidden but Discoverable (Unlimited)
- Materials
- Modifiers
- Animation
- Advanced mesh editing
- Constraints
- Physics
- Rendering

---

## 💡 USAGE PATTERNS

### User asks: "How do I add materials?"
```
Claude → search_tools(query="material")
Claude → Discovers set_material tool
Claude → Uses it
```

### User asks: "What lighting tools are available?"
```
Claude → search_tools(category="lighting")
Claude → Lists all lighting tools
Claude → Explains capabilities
```

### User asks: "Show me all available tools"
```
Claude → search_tools(show_hidden=True)
Claude → Returns complete catalog
Claude → Groups by category
```

---

## 🎯 BENEFITS

✅ **Scalability**: Unlimited tools without hitting 30 limit
✅ **Discoverability**: Search makes hidden tools findable
✅ **Organization**: Categories provide structure
✅ **Cleanliness**: UI not cluttered with rarely-used tools
✅ **Flexibility**: Easy to add new tools without reorganizing
✅ **Documentation**: Metadata provides examples/usage

---

## 📝 NEXT STEPS

1. ✅ Design complete
2. → Implement `search_tools` in bridge
3. → Add TOOL_METADATA dict
4. → Test search functionality
5. → Add to MCP server
6. → Document for users
7. → Continue with `create_primitive`

---

**Status:** Design complete, ready for implementation
