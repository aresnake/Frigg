# Frigg MCP Tools - Priority & Organization Strategy

**Constraint:** Maximum 30 tools visible in MCP
**Current count:** ~10 tools (scene_info, list_objects, transforms, viewport_snapshot, etc.)

---

## 🎯 CORE PHILOSOPHY

**The 80/20 rule:** 20% of tools will be used 80% of the time.

These must be VISIBLE. Everything else can be hidden behind flags or combined into meta-tools.

---

## 📊 TIER 1: ALWAYS VISIBLE (Essential - ~15 tools)

### VISION (3 tools)
1. ✅ **viewport_snapshot** - See the scene (with all view options)
2. ✅ **get_bounding_box** - Measure dimensions
3. ✅ **get_spatial_relationships** - Understand positions

### SPATIAL QUERY (2 tools)
4. ✅ **scene_info** - What's in the scene
5. ✅ **list_objects** - All objects with types

### BASIC TRANSFORMS (4 tools) ✅ COMPLETE
6. ✅ **get_object_transform** - Read position/rotation/scale
7. ✅ **set_object_location** - Move object
8. ✅ **set_object_rotation** - Rotate object (v0.10)
9. ✅ **set_object_scale** - Scale object (v0.10)

### CREATION (4 tools)
10. **create_cube** - Most common primitive
11. **create_sphere** - Second most common
12. **create_cylinder** - Third most common
13. **create_empty** - Organizational helper

### ESSENTIAL OPERATIONS (3 tools)
14. **duplicate_object** - Copy objects
15. **delete_object** - Remove objects
16. **rename_object** - Better organization

---

## 📦 TIER 2: GROUPED/META TOOLS (Consolidate - ~8 tools)

### Option A: Group by primitive type
17. **create_primitive** - One tool with type parameter
   ```python
   {
       "primitive_type": "cube|sphere|cylinder|cone|torus|plane",
       "name": "MyObject",
       "location": [0, 0, 0],
       "scale": [1, 1, 1]
   }
   ```

### Option B: Material operations (grouped)
18. **set_material** - Create and assign materials
   ```python
   {
       "object_name": "Cube",
       "material_name": "Red",
       "color": [1, 0, 0, 1],
       "metallic": 0.0,
       "roughness": 0.5
   }
   ```

### Advanced vision (when needed)
19. **render_camera** - Final quality renders (not viewport)

### Boolean operations (grouped)
20. **boolean_operation** - union|difference|intersect in one tool

### Modifiers (grouped)
21. **add_modifier** - array|mirror|solidify|bevel|subdivision in one tool

### Parent/hierarchy
22. **set_parent** - Object hierarchy
23. **clear_parent** - Unparent

### Selection operations
24. **select_objects** - Multi-select
25. **deselect_all** - Clear selection

---

## 🔒 TIER 3: HIDDEN BY DEFAULT (Advanced/Rare - unlimited)

**Access via:**
- Environment variable flag: `FRIGG_ADVANCED_TOOLS=1`
- Or specific flag per category: `FRIGG_SHOW_ANIMATION=1`

### Animation tools (rarely needed for modeling)
- **keyframe_insert**
- **keyframe_delete**
- **set_frame**

### Mesh editing (advanced)
- **edit_mesh_vertices**
- **extrude_faces**
- **subdivide_mesh**

### Lighting (specific use case)
- **create_light**
- **set_light_properties**

### Camera operations (specific use case)
- **create_camera**
- **set_camera_properties**

### Constraints (advanced)
- **add_constraint**

### Collections (organization - not essential)
- **create_collection**
- **link_to_collection**

---

## 🎨 RECOMMENDED VISIBLE SET (30 tools max)

### CURRENT STATUS: ~13 tools (v0.10)
1. ✅ frigg.ping
2. ✅ frigg.blender.scene_info
3. ✅ frigg.blender.bridge_ping
4. ✅ frigg.blender.get_object_transform
5. ✅ frigg.blender.set_object_location
6. ✅ frigg.blender.set_object_rotation **NEW v0.10**
7. ✅ frigg.blender.set_object_scale **NEW**
8. ✅ frigg.blender.list_objects
9. ✅ frigg.blender.move_object (duplicate of set_object_location?)
10. ✅ frigg.blender.viewport_snapshot
11. ✅ frigg.blender.get_bounding_box
12. ✅ frigg.blender.get_spatial_relationships
13. ✅ frigg.blender.measure_distance (if exists)

### NEXT TO ADD: 7 tools (Priority order - 17 slots remaining)
14. **create_primitive** (cube/sphere/cylinder/cone/plane/torus) **← HIGHEST PRIORITY**
15. **duplicate_object** (essential for modeling)
16. **delete_object** (cleanup)
17. **rename_object** (organization)
18. **set_material** (visual quality)
19. **set_parent** (hierarchy)
20. **boolean_operation** (CSG modeling)

### BUFFER: 10 slots remaining (30 limit)
21. **create_empty** (helpers)
22. **add_modifier** (array, mirror, etc.)
23. **select_objects** (multi-select)
24. **render_camera** (final output)
25. **create_light** (lighting)
26. **create_camera** (camera setup)
27-30. Reserved for user requests

---

## 🚀 IMPLEMENTATION STRATEGY

### ✅ Phase 1: Complete Basic Transforms (DONE v0.10)
- ✅ `set_object_scale`
- ✅ `set_object_rotation`

### Phase 2: Creation Tools (CURRENT - HIGH PRIORITY)
- `create_primitive` (with type parameter - one tool for all)

### Phase 3: Essential Operations (MEDIUM)
- `duplicate_object`
- `delete_object`
- `rename_object`

### Phase 4: Visual Quality (MEDIUM)
- `set_material` (grouped - create + assign in one)

### Phase 5: Advanced Modeling (LOW)
- `boolean_operation`
- `add_modifier`

---

## 💡 KEY DECISIONS

### 1. Consolidate primitives into ONE tool
❌ create_cube, create_sphere, create_cylinder, create_cone, create_torus (5 tools)
✅ create_primitive with type parameter (1 tool)

### 2. Keep transforms separate (frequently used differently)
✅ set_object_location (position)
✅ set_object_rotation (orientation)
✅ set_object_scale (size)

### 3. Material system = one tool
❌ create_material, assign_material, set_color, set_metallic (4 tools)
✅ set_material (creates if needed, assigns, sets all properties) (1 tool)

### 4. Advanced features = flag-gated
- Animation tools: `FRIGG_SHOW_ANIMATION=1`
- Mesh editing: `FRIGG_SHOW_MESH_EDIT=1`
- All advanced: `FRIGG_ADVANCED_TOOLS=1`

---

## 📋 FINAL COUNT

- **Tier 1 visible:** 20 tools (essentials)
- **Tier 2 visible:** 10 tools (frequently used)
- **Tier 3 hidden:** Unlimited (flag-gated)
- **Total visible:** 30 tools (at limit)

---

## 🎯 NEXT ACTIONS

1. Implement `set_object_rotation` (complete transforms)
2. Implement `set_object_scale` (complete transforms)
3. Implement `create_primitive` (unified creation)
4. Implement `duplicate_object` (essential for workflow)
5. Implement `delete_object` (cleanup)

Then reassess based on actual usage patterns.

---

**Philosophy:** Start lean, add based on real needs, hide complexity behind flags.
