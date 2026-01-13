# CODEX MEGA-PROMPT: Generate Frigg MCP Blender Tools

## Context
You are generating Python functions for a Blender MCP (Model Context Protocol) server. These tools will be called by an AI assistant (Claude) to perform 3D modeling operations in Blender.

## Architecture Overview

### File Structure
```
src/frigg_mcp/tools/
├── core_tools.py          # Primitives, transforms, cameras
├── modifier_tools.py      # Modifiers (Mirror, Array, Boolean, etc.)
├── material_tools.py      # Materials and shading
├── collection_tools.py    # Collections and organization
├── mesh_editing_tools.py  # NEW: Mesh editing operations
├── edge_tools.py          # NEW: Edge operations
├── inspection_tools.py    # NEW: Inspection and validation
└── uv_tools.py           # NEW: UV mapping operations
```

### Existing Pattern (Reference)

Here's how existing tools are structured:

```python
# In src/frigg_mcp/tools/core_tools.py

@mcp.tool()
async def frigg_blender_create_primitive(
    type: str,
    name: Optional[str] = None,
    location: Optional[List[float]] = None,
    rotation: Optional[List[float]] = None,
    scale: Optional[float] = None,
    size: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a primitive object (cube, sphere, cylinder, cone, torus, plane, monkey).

    Args:
        type: Primitive type (CUBE, SPHERE, CYLINDER, CONE, TORUS, PLANE, MONKEY)
        name: Optional name for the object
        location: [x, y, z] position
        rotation: [x, y, z] rotation in degrees
        scale: Uniform scale factor
        size: Size of the primitive

    Returns:
        Object creation info with name, location, rotation, scale
    """
    cmd = {
        "action": "create_primitive",
        "type": type.upper(),
        "name": name,
        "location": location or [0, 0, 0],
        "rotation": rotation or [0, 0, 0],
        "scale": scale,
        "size": size
    }

    result = await send_blender_command(cmd)
    return result
```

### Bridge Handler Pattern (Reference)

```python
# In blender_bridge_addon/__init__.py

def handle_create_primitive(data):
    """Handler for create_primitive command"""
    prim_type = data.get("type", "CUBE")
    name = data.get("name")
    location = data.get("location", [0, 0, 0])
    rotation_deg = data.get("rotation", [0, 0, 0])
    scale_val = data.get("scale", 1.0)
    size = data.get("size", 2.0)

    # Create primitive
    if prim_type == "CUBE":
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    elif prim_type == "SPHERE":
        bpy.ops.mesh.primitive_uv_sphere_add(radius=size/2, location=location)
    # ... etc

    obj = bpy.context.active_object

    # Apply transformations
    if name:
        obj.name = name

    obj.rotation_euler = [math.radians(r) for r in rotation_deg]
    obj.scale = [scale_val] * 3

    return {
        "name": obj.name,
        "type": prim_type.lower(),
        "location": list(obj.location),
        "rotation_degrees": rotation_deg,
        "scale": list(obj.scale)
    }

# Register handler
COMMAND_HANDLERS = {
    "create_primitive": handle_create_primitive,
    # ... other handlers
}
```

## Your Mission

Generate **complete, production-ready code** for the following tool categories. Each category should include:

1. **MCP Tool definitions** (async functions with @mcp.tool() decorator)
2. **Bridge handlers** (sync functions that execute in Blender)
3. **Complete error handling**
4. **Detailed docstrings**
5. **Type hints**

---

## BATCH 1: MESH EDITING TOOLS

### File: `src/frigg_mcp/tools/mesh_editing_tools.py`

Create these tools:

#### 1. `frigg_blender_join_objects`
- **Purpose**: Merge multiple mesh objects into one
- **Parameters**:
  - `object_names: List[str]` - List of object names to join
  - `result_name: Optional[str]` - Name for the resulting object
- **Returns**: `{result_object, vertex_count, face_count, merged_objects}`
- **Bridge action**: `"join_objects"`

#### 2. `frigg_blender_extrude_faces`
- **Purpose**: Extrude selected faces
- **Parameters**:
  - `object_name: str`
  - `face_indices: Union[List[int], str]` - List of indices or "all"
  - `offset: float = 0.5`
  - `direction: Optional[List[float]]` - [x,y,z] direction (None = normals)
- **Returns**: `{object, extruded_faces, new_vertex_count}`
- **Bridge action**: `"extrude_faces"`

#### 3. `frigg_blender_inset_faces`
- **Purpose**: Create insets on faces (for details like planks)
- **Parameters**:
  - `object_name: str`
  - `face_indices: Optional[List[int]]` - None = all faces
  - `thickness: float = 0.1`
  - `depth: float = 0.0`
- **Returns**: `{object, inset_faces, new_face_count}`
- **Bridge action**: `"inset_faces"`

#### 4. `frigg_blender_merge_vertices`
- **Purpose**: Merge vertices by distance (remove doubles)
- **Parameters**:
  - `object_name: str`
  - `distance: float = 0.0001`
- **Returns**: `{object, vertices_before, vertices_after, removed_count}`
- **Bridge action**: `"merge_vertices"`

### Bridge Handlers for BATCH 1

In `blender_bridge_addon/__init__.py`, add handlers:

```python
def handle_join_objects(data):
    """Join multiple mesh objects"""
    # Implementation here
    pass

def handle_extrude_faces(data):
    """Extrude faces"""
    # Implementation here
    pass

def handle_inset_faces(data):
    """Inset faces"""
    # Implementation here
    pass

def handle_merge_vertices(data):
    """Merge vertices by distance"""
    # Implementation here
    pass
```

---

## BATCH 2: EDGE OPERATIONS

### File: `src/frigg_mcp/tools/edge_tools.py`

#### 1. `frigg_blender_bevel_edges` ⭐ CRITICAL
- **Purpose**: Bevel/chamfer edges (essential for realism)
- **Parameters**:
  - `object_name: str`
  - `edge_indices: Optional[List[int]]` - None = all edges
  - `width: float = 0.1`
  - `segments: int = 2`
  - `profile: float = 0.5`
- **Returns**: `{object, beveled_edges, new_vertex_count, segments}`
- **Bridge action**: `"bevel_edges"`

#### 2. `frigg_blender_subdivide_mesh`
- **Purpose**: Subdivide geometry
- **Parameters**:
  - `object_name: str`
  - `cuts: int = 1`
  - `smooth: float = 0.0`
- **Returns**: `{object, vertices_before, vertices_after, cuts}`
- **Bridge action**: `"subdivide_mesh"`

#### 3. `frigg_blender_bridge_edge_loops`
- **Purpose**: Connect two edge loops with faces
- **Parameters**:
  - `object_name: str`
  - `edge_loop_1: List[int]`
  - `edge_loop_2: List[int]`
- **Returns**: `{object, faces_created, bridged_edges}`
- **Bridge action**: `"bridge_edge_loops"`

---

## BATCH 3: INSPECTION TOOLS

### File: `src/frigg_mcp/tools/inspection_tools.py`

#### 1. `frigg_blender_get_mesh_stats`
- **Purpose**: Get detailed mesh statistics
- **Parameters**:
  - `object_name: str`
- **Returns**: `{object, vertices, edges, faces, triangles, ngons, has_loose_verts, has_loose_edges}`
- **Bridge action**: `"get_mesh_stats"`

#### 2. `frigg_blender_get_object_bounds`
- **Purpose**: Get object dimensions and bounding box
- **Parameters**:
  - `object_name: str`
  - `world_space: bool = True`
- **Returns**: `{object, dimensions, center, min_bound, max_bound, volume}`
- **Bridge action**: `"get_object_bounds"`

#### 3. `frigg_blender_validate_mesh`
- **Purpose**: Validate mesh quality and detect errors
- **Parameters**:
  - `object_name: str`
  - `fix_issues: bool = False`
- **Returns**: `{object, is_valid, issues, non_manifold_edges, degenerate_faces, fixed}`
- **Bridge action**: `"validate_mesh"`

#### 4. `frigg_blender_check_uvs`
- **Purpose**: Check if object has UVs
- **Parameters**:
  - `object_name: str`
- **Returns**: `{object, has_uvs, uv_layers, uv_layer_names, faces_with_uvs, faces_without_uvs}`
- **Bridge action**: `"check_uvs"`

---

## BATCH 4: UV MAPPING

### File: `src/frigg_mcp/tools/uv_tools.py`

#### 1. `frigg_blender_unwrap_uv_smart`
- **Purpose**: Smart UV unwrap
- **Parameters**:
  - `object_name: str`
  - `angle_limit: float = 66.0`
  - `island_margin: float = 0.0`
- **Returns**: `{object, uv_layer_name, island_count}`
- **Bridge action**: `"unwrap_uv_smart"`

#### 2. `frigg_blender_unwrap_uv_cube`
- **Purpose**: Cube projection unwrap (good for boxes)
- **Parameters**:
  - `object_name: str`
  - `cube_size: float = 1.0`
- **Returns**: `{object, uv_layer_name, projection_type}`
- **Bridge action**: `"unwrap_uv_cube"`

---

## BATCH 5: EXPORT TOOLS

### File: `src/frigg_mcp/tools/export_tools.py`

#### 1. `frigg_blender_export_fbx`
- **Purpose**: Export selected objects to FBX
- **Parameters**:
  - `filepath: str`
  - `object_names: Optional[List[str]]` - None = all selected
  - `apply_modifiers: bool = True`
  - `use_mesh_modifiers: bool = True`
- **Returns**: `{filepath, exported_objects, file_size}`
- **Bridge action**: `"export_fbx"`

#### 2. `frigg_blender_export_gltf`
- **Purpose**: Export to GLTF/GLB format
- **Parameters**:
  - `filepath: str`
  - `export_format: str = "GLB"` - GLB or GLTF
  - `object_names: Optional[List[str]]`
- **Returns**: `{filepath, exported_objects, file_size, format}`
- **Bridge action**: `"export_gltf"`

#### 3. `frigg_blender_apply_all_transforms`
- **Purpose**: Apply location, rotation, scale to selected objects
- **Parameters**:
  - `object_names: List[str]`
  - `location: bool = True`
  - `rotation: bool = True`
  - `scale: bool = True`
- **Returns**: `{applied_objects, transforms_applied}`
- **Bridge action**: `"apply_all_transforms"`

---

## Code Generation Requirements

### For MCP Tools:
1. Import `mcp` from `mcp.server`
2. Use `@mcp.tool()` decorator
3. Make functions `async`
4. Import types: `Dict, Any, List, Optional, Union`
5. Call `await send_blender_command(cmd)` to send to bridge
6. Add comprehensive docstrings
7. Include error handling

### For Bridge Handlers:
1. Use `bpy` operations
2. Switch to EDIT mode when needed with `bpy.ops.object.mode_set(mode='EDIT')`
3. Always return to OBJECT mode before returning
4. Handle selection properly with `select_all`, `select_set`
5. Return dict with results
6. Include try/except blocks
7. Validate inputs (object exists, correct type, etc.)

### Error Handling Pattern:
```python
# MCP side
if "error" in result:
    return {"error": result["error"]}

# Bridge side
try:
    # operations
    return {"success": True, ...}
except Exception as e:
    return {"error": str(e)}
```

---

## Output Format

For each BATCH, generate:

### 1. MCP Tools File
```python
# src/frigg_mcp/tools/[category]_tools.py

from mcp.server import Server
from typing import Dict, Any, List, Optional, Union
from ..bridge import send_blender_command

mcp = Server("frigg")

@mcp.tool()
async def frigg_blender_[tool_name](...) -> Dict[str, Any]:
    """Docstring"""
    cmd = {"action": "...", ...}
    result = await send_blender_command(cmd)
    return result
```

### 2. Bridge Handlers (to add to __init__.py)
```python
# blender_bridge_addon/__init__.py additions

def handle_[action_name](data):
    """Handler for [action_name]"""
    try:
        # Implementation
        return {"success": True, ...}
    except Exception as e:
        return {"error": str(e)}

# Add to COMMAND_HANDLERS dict
COMMAND_HANDLERS = {
    # ... existing
    "[action_name]": handle_[action_name],
}
```

---

## Generate Code Now

Generate complete, production-ready code for **ALL 5 BATCHES** with:

✅ Complete MCP tool files
✅ Complete bridge handler implementations
✅ Full error handling
✅ Detailed docstrings
✅ Type hints
✅ Input validation
✅ Mode switching (EDIT/OBJECT)
✅ Selection handling
✅ Proper return values

**IMPORTANT**: Generate COMPLETE, WORKING code that can be copy-pasted directly into the files. Don't use placeholders or "TODO" comments. Every function should be fully implemented.

Start with BATCH 1 (Mesh Editing Tools) and generate the complete code now.
