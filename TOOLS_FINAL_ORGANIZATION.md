# Frigg MCP - Final Tool Organization (30 Visible Tools)

**Version:** v1.0 Final
**Date:** 2026-01-12
**Philosophy:** The 30 most essential tools for 3D modeling workflow

---

## 🎯 THE 30 VISIBLE TOOLS (Prioritized)

### 🔧 CORE UTILITIES (3 tools)
1. ✅ **frigg.ping** - Health check
2. ✅ **frigg.search_tools** - Discover hidden tools ⭐
3. ✅ **frigg.blender.bridge_ping** - Bridge health check

### 📊 SCENE QUERY (3 tools)
4. ✅ **frigg.blender.scene_info** - Scene metadata
5. ✅ **frigg.blender.list_objects** - All objects with types
6. **frigg.blender.get_selected** - Get currently selected objects

### 🎨 TRANSFORMS (5 tools) ✅ COMPLETE
7. ✅ **frigg.blender.get_object_transform** - Read transform
8. ✅ **frigg.blender.set_object_location** - Move object
9. ✅ **frigg.blender.set_object_rotation** - Rotate object
10. ✅ **frigg.blender.set_object_scale** - Scale object
11. **frigg.blender.apply_transform** - Bake transforms

### 👁️ VISION (3 tools) ✅ COMPLETE
12. ✅ **frigg.blender.viewport_snapshot** - See the scene
13. ✅ **frigg.blender.get_bounding_box** - Measure dimensions
14. ✅ **frigg.blender.get_spatial_relationships** - Understand positions

### ➕ CREATION (4 tools)
15. ✅ **frigg.blender.create_primitive** - Cube/sphere/cylinder/etc
16. **frigg.blender.duplicate_object** - Copy objects ⭐
17. **frigg.blender.create_empty** - Helper/parent objects
18. **frigg.blender.create_camera** - Camera setup

### 🗑️ ESSENTIAL OPERATIONS (4 tools)
19. **frigg.blender.delete_object** - Remove objects ⭐
20. **frigg.blender.rename_object** - Organization ⭐
21. **frigg.blender.select_object** - Selection management
22. **frigg.blender.hide_object** - Toggle visibility

### 🎭 MATERIALS & APPEARANCE (2 tools)
23. **frigg.blender.set_material** - Create/assign material ⭐
24. **frigg.blender.set_smooth_shading** - Smooth vs flat shading

### 🔗 HIERARCHY & ORGANIZATION (2 tools)
25. **frigg.blender.set_parent** - Parent/child relationships ⭐
26. **frigg.blender.clear_parent** - Unparent objects

### 🔨 MODIFIERS (2 tools)
27. **frigg.blender.add_modifier** - Array/mirror/subdivision/etc
28. **frigg.blender.apply_modifier** - Bake modifier

### 💡 LIGHTING (1 tool)
29. **frigg.blender.create_light** - Point/sun/spot/area lights

### 🎬 OUTPUT (1 tool)
30. **frigg.blender.render_camera** - Final render output

**Total: 30 tools (at limit)**

⭐ = Highest priority to implement next

---

## 📦 HIDDEN TOOLS (Discoverable via search_tools)

### Category: `mesh_editing` (Advanced)
- **edit_mesh** - Enter edit mode and modify vertices
- **extrude_faces** - Extrude selected faces
- **subdivide_mesh** - Subdivide geometry
- **merge_vertices** - Merge selected verts
- **dissolve_edges** - Remove edges

### Category: `modifiers_advanced` (Specialized)
- **add_boolean_modifier** - Boolean union/difference/intersect
- **add_solidify_modifier** - Give thickness to surfaces
- **add_bevel_modifier** - Round edges
- **add_skin_modifier** - Organic modeling

### Category: `animation` (Time-based)
- **keyframe_insert** - Set keyframe
- **keyframe_delete** - Remove keyframe
- **set_frame** - Change current frame
- **bake_animation** - Bake to keyframes

### Category: `constraints` (Rigging)
- **add_constraint** - Track to, copy location, etc
- **remove_constraint** - Remove constraint

### Category: `materials_advanced` (Shading)
- **create_material** - Create material (without assigning)
- **get_material** - Get material properties
- **add_texture** - Add image texture
- **create_shader_node** - Node-based shading

### Category: `lighting_advanced` (Studio)
- **set_light_properties** - Intensity, color, radius
- **set_light_color** - RGB color
- **create_area_light** - Soft lighting

### Category: `camera_advanced` (Cinematography)
- **set_camera_properties** - FOV, sensor, clip
- **camera_look_at** - Aim camera at object
- **create_camera_constraint** - Track to constraint

### Category: `rendering` (Output)
- **set_render_settings** - Resolution, samples, format
- **render_animation** - Render frame sequence
- **set_world_properties** - Background color/HDRI

### Category: `collections` (Organization)
- **create_collection** - New collection
- **link_to_collection** - Add object to collection
- **unlink_from_collection** - Remove from collection

### Category: `physics` (Simulation)
- **add_physics** - Rigid body, cloth, fluid
- **bake_physics** - Bake simulation
- **set_collision** - Collision properties

### Category: `import_export` (File I/O)
- **import_obj** - Import OBJ file
- **export_obj** - Export to OBJ
- **import_fbx** - Import FBX
- **export_fbx** - Export to FBX
- **export_stl** - Export for 3D printing

---

## 🏷️ TAG SYSTEM (for search_tools)

### By Action Verb
- **create**: create_primitive, create_camera, create_light, create_empty, create_material
- **set**: set_location, set_rotation, set_scale, set_material, set_parent
- **get**: get_transform, get_bounding_box, get_spatial_relationships, get_selected
- **add**: add_modifier, add_constraint, add_physics
- **apply**: apply_transform, apply_modifier
- **delete**: delete_object
- **duplicate**: duplicate_object
- **render**: viewport_snapshot, render_camera, render_animation

### By Domain
- **transform**: location, rotation, scale, apply_transform
- **vision**: viewport_snapshot, bounding_box, spatial_relationships
- **material**: set_material, create_material, get_material, smooth_shading
- **lighting**: create_light, set_light_properties, set_light_color
- **camera**: create_camera, set_camera_properties, look_at
- **hierarchy**: set_parent, clear_parent
- **modifier**: add_modifier, apply_modifier, boolean, bevel, array

### By Complexity
- **simple**: Most visible tools (beginner-friendly)
- **medium**: Modifiers, materials, constraints
- **advanced**: Mesh editing, node shading, physics

---

## 🚀 IMPLEMENTATION ROADMAP

### Phase 3: Essential Operations (NEXT - 4 tools)
**Priority: HIGHEST** - Can't model without these
1. **duplicate_object** - Copy workflow essential
2. **delete_object** - Cleanup essential
3. **rename_object** - Organization essential
4. **select_object** - Selection management

**Estimated: 1-2 hours implementation**

### Phase 4: Materials & Hierarchy (3 tools)
**Priority: HIGH** - Visual quality + organization
1. **set_material** - Colors and appearance
2. **set_parent** - Object hierarchy
3. **set_smooth_shading** - Surface quality

**Estimated: 2-3 hours implementation**

### Phase 5: Fill to 30 (Remaining 9 tools)
**Priority: MEDIUM** - Complete the visible set
- create_empty
- hide_object
- clear_parent
- add_modifier
- apply_modifier
- apply_transform
- create_light
- create_camera
- render_camera
- get_selected

**Estimated: 4-6 hours implementation**

### Phase 6: Hidden Tools (Unlimited)
**Priority: LOW** - Add as needed
- Implement based on user requests
- Discoverable via search_tools
- No rush, add when specific use cases arise

---

## 📐 TOOL NAMING CONVENTION

### Prefix Structure
```
frigg.                     # Core utilities (ping, search)
frigg.blender.             # All Blender operations
```

### Verb Guidelines
- **create_** - Creates new object/data
- **get_** - Reads information
- **set_** - Modifies existing property
- **add_** - Adds component to object
- **apply_** - Bakes/finalizes
- **delete_** - Removes
- **duplicate_** - Copies
- **render_** - Generates image/video

### Consistent Parameters
```python
# Object identification
object_name: str         # Always primary identifier

# Transform
location: [x, y, z]      # World space position
rotation: [x, y, z]      # Degrees (converted to radians internally)
scale: float | [x,y,z]   # Uniform or per-axis

# Common options
name: str                # Custom name
```

---

## 🎓 USER WORKFLOW EXAMPLES

### Beginner Workflow (Visible tools only)
```
1. create_primitive(type="cube")
2. set_object_location(object_name="Cube", location=[2, 0, 0])
3. set_object_scale(object_name="Cube", scale=1.5)
4. duplicate_object(object_name="Cube", name="Cube2")
5. set_material(object_name="Cube", color=[1, 0, 0, 1])
6. viewport_snapshot(view="front", projection="ortho")
```

### Intermediate Workflow (Using search)
```
User: "How do I make smooth surfaces?"
→ search_tools(query="smooth")
→ Finds: set_smooth_shading

User: "I need to create a pattern of objects"
→ search_tools(query="array")
→ Finds: add_modifier (with array type)
```

### Advanced Workflow (Hidden tools)
```
User: "I want to do boolean operations"
→ search_tools(query="boolean", show_hidden=True)
→ Finds: add_boolean_modifier

User: "Export for 3D printing"
→ search_tools(query="export stl", show_hidden=True)
→ Finds: export_stl
```

---

## 💡 DESIGN DECISIONS

### Why 30 tools visible?
- MCP has performance/UI limits around 30-40 tools
- 30 covers 90% of common modeling workflows
- Keeps UI clean and discoverable
- Advanced users can search for more

### Why search_tools is visible?
- **It unlocks all hidden tools**
- Acts as a "More tools..." button
- Provides documentation and examples
- Essential for discovering capabilities

### Why these specific 30?
1. **Frequency analysis** - Most used in typical 3D workflow
2. **Workflow completeness** - Create → Transform → Organize → Output
3. **Beginner friendliness** - Simple, intuitive operations first
4. **Power user escape hatch** - search_tools for advanced needs

### Category Distribution (30 tools)
- Core: 3 (10%)
- Query: 3 (10%)
- Transform: 5 (17%)
- Vision: 3 (10%)
- Creation: 4 (13%)
- Operations: 4 (13%)
- Materials: 2 (7%)
- Hierarchy: 2 (7%)
- Modifiers: 2 (7%)
- Lighting: 1 (3%)
- Output: 1 (3%)

**Balanced across workflow stages** ✅

---

## 📊 CURRENT STATUS

**Implemented: 14/30 tools (47%)**

✅ Core: 3/3 (100%)
✅ Query: 2/3 (67%)
✅ Transform: 4/5 (80%)
✅ Vision: 3/3 (100%)
✅ Creation: 1/4 (25%)
❌ Operations: 0/4 (0%) ← NEXT PRIORITY
❌ Materials: 0/2 (0%)
❌ Hierarchy: 0/2 (0%)
❌ Modifiers: 0/2 (0%)
❌ Lighting: 0/1 (0%)
❌ Output: 0/1 (0%)

**Next 3 tools to implement:**
1. duplicate_object
2. delete_object
3. rename_object

**ETA to 30 tools:** ~6-8 hours development time

---

## 🎯 SUCCESS METRICS

**When complete, Claude will be able to:**
- ✅ See the 3D scene (vision tools)
- ✅ Create basic objects (primitives)
- ✅ Transform objects freely (location/rotation/scale)
- ✅ Understand spatial relationships
- ⏳ Copy and organize objects (duplicate/rename/delete)
- ⏳ Apply materials and colors
- ⏳ Set up hierarchy (parent/child)
- ⏳ Use modifiers for complex shapes
- ⏳ Light and render the scene
- ✅ Discover advanced tools via search

**= Complete 3D modeling capability** 🎉

---

**Status:** Ready to implement Phase 3 (Essential Operations)
