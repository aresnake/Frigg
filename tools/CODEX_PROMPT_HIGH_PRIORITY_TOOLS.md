# Codex Prompt: Implement 3 HIGH Priority Mesh Tools

## Context
You are implementing 3 critical mesh editing tools for the Frigg Blender MCP bridge. Follow the EXACT pattern used by existing tools to ensure 0 errors.

## Reference Implementation (WORKING)
```python
def extrude_faces(params):
    """Extrude faces on a mesh object."""
    import bmesh

    try:
        object_name = params.get("object_name")
        face_indices = params.get("face_indices")
        offset = params.get("offset", 0.5)
        direction = params.get("direction")

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        # Enter edit mode
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        # Select faces using bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if face_indices is None or face_indices == "all":
            for face in bm.faces:
                face.select = True
            selected_faces = [face.index for face in bm.faces]
        elif isinstance(face_indices, list):
            try:
                indices = {int(i) for i in face_indices}
            except (TypeError, ValueError):
                raise ValueError("face_indices must be a list of integers.")
            selected_faces = []
            for face in bm.faces:
                face.select = face.index in indices
                if face.select:
                    selected_faces.append(face.index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        # Perform operation
        bpy.ops.mesh.extrude_region()
        bpy.ops.transform.shrink_fatten(value=float(offset))

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "extruded_faces": selected_faces,
            "new_vertex_count": len(obj.data.vertices),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
```

## Task: Implement These 3 Functions

### 1. bevel_edges
```python
def bevel_edges(params):
    """Bevel edges on a mesh object."""
    # REQUIRED params:
    # - object_name: str
    # - edge_indices: list[int] | "all" | None (all edges if None)
    # - width: float (default: 0.1)
    # - segments: int (default: 2)
    # - profile: float (default: 0.5, range 0-1)

    # MUST follow this pattern:
    # 1. Import bmesh
    # 2. try/finally with mode_set cleanup
    # 3. Validate object_name, get obj, check MESH type
    # 4. Enter OBJECT mode, deselect all, select obj, set active
    # 5. Enter EDIT mode, deselect all
    # 6. Use bmesh to select edges (bm.edges.ensure_lookup_table())
    # 7. bmesh.update_edit_mesh before operation
    # 8. Call bpy.ops.mesh.bevel(offset=width, segments=segments, profile=profile)
    # 9. bmesh.update_edit_mesh after operation
    # 10. Return dict with: object, beveled_edges, new_vertex_count
    # 11. finally: return to OBJECT mode
```

### 2. subdivide_mesh
```python
def subdivide_mesh(params):
    """Subdivide mesh faces."""
    # REQUIRED params:
    # - object_name: str
    # - cuts: int (default: 1, range 1-10)
    # - smooth: float (default: 0.0, range 0-1)
    # - face_indices: list[int] | None (all faces if None)

    # MUST follow same pattern as extrude_faces:
    # 1. Import bmesh
    # 2. try/finally with mode_set cleanup
    # 3. Validate object, enter EDIT mode
    # 4. Use bmesh to select faces (bm.faces.ensure_lookup_table())
    # 5. bmesh.update_edit_mesh before operation
    # 6. Call bpy.ops.mesh.subdivide(number_cuts=cuts, smoothness=smooth)
    # 7. bmesh.update_edit_mesh after operation
    # 8. Return dict with: object, subdivided_faces, new_vertex_count, new_face_count
    # 9. finally: return to OBJECT mode
```

### 3. recalculate_normals
```python
def recalculate_normals(params):
    """Recalculate face normals (fix inside-out faces)."""
    # REQUIRED params:
    # - object_name: str
    # - inside: bool (default: False) - if True, normals point inside

    # MUST follow same pattern:
    # 1. Import bmesh
    # 2. try/finally with mode_set cleanup
    # 3. Validate object, enter EDIT mode
    # 4. Select ALL mesh elements: bpy.ops.mesh.select_all(action="SELECT")
    # 5. Call bpy.ops.mesh.normals_make_consistent(inside=inside)
    # 6. Return dict with: object, status="recalculated", face_count
    # 7. finally: return to OBJECT mode
```

## Critical Requirements for 0 Errors

### MUST DO:
1. ✅ Import bmesh at start of try block
2. ✅ Validate all required params before any operation
3. ✅ Check obj exists and obj.type == "MESH"
4. ✅ ALWAYS use try/finally with mode_set(mode="OBJECT") in finally
5. ✅ Use bpy.ops.object.mode_set(mode="OBJECT") then mode_set(mode="EDIT")
6. ✅ Use bmesh.from_edit_mesh(obj.data) for edge/face selection
7. ✅ Call .ensure_lookup_table() before accessing by index
8. ✅ Call bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False) before AND after operations
9. ✅ Use float() for numeric params passed to operators
10. ✅ Return dict with meaningful data (counts, indices, etc.)

### MUST NOT DO:
❌ Use bpy.ops.object.mode_set without try/finally
❌ Access edges/faces without ensure_lookup_table()
❌ Forget bmesh.update_edit_mesh calls
❌ Use mesh.update() instead of bmesh.update_edit_mesh()
❌ Pass params to operators without float() conversion
❌ Raise exceptions without validation
❌ Use shortcuts or skip steps

## Implementation Pattern Template
```python
def tool_name(params):
    """Tool description."""
    import bmesh

    try:
        # 1. Extract and validate params
        object_name = params.get("object_name")
        if not object_name:
            raise ValueError("object_name is required.")

        # 2. Get and validate object
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        # 3. Enter edit mode properly
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        # 4. Use bmesh for selection (if needed)
        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()  # or bm.faces

        # ... selection logic ...

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        # 5. Perform operation
        bpy.ops.mesh.operation_name(param=float(value))

        # 6. Update mesh
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        # 7. Return result
        return {
            "object": obj.name,
            "status": "success",
            "vertex_count": len(obj.data.vertices)
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
```

## Output Format
Provide ONLY the 3 complete function implementations.
No explanations, no comments except docstrings.
Each function must be production-ready, tested pattern.

## Validation Checklist (Each Function)
- [ ] Imports bmesh
- [ ] Has try/finally block
- [ ] Validates object_name
- [ ] Checks obj.type == "MESH"
- [ ] Enters OBJECT mode first
- [ ] Enters EDIT mode correctly
- [ ] Uses bmesh for selection
- [ ] Calls ensure_lookup_table()
- [ ] Updates mesh before operation
- [ ] Updates mesh after operation
- [ ] Returns meaningful dict
- [ ] Returns to OBJECT mode in finally
