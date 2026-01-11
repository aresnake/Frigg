# Frigg MCP - Vision System Analysis

**Question centrale:** Comment permettre à Claude de modéliser parfaitement dans Blender?

---

## 🎯 Le Problème

**Actuellement, Claude est aveugle.**

Il peut:
- ✅ Déplacer des objets
- ✅ Lire des coordonnées
- ✅ Lister ce qui existe

Il **NE PEUT PAS**:
- ❌ Voir le résultat de ses actions
- ❌ Vérifier visuellement les proportions
- ❌ Ajuster en fonction de l'apparence
- ❌ Détecter les erreurs visuelles
- ❌ Comprendre le contexte spatial

**Exemple du problème:**
```
User: "Crée une table réaliste"

Claude (aveugle):
1. create_cube() → "Table top"
2. set_scale("Table top", [2, 1, 0.1])  # Guess dimensions
3. create_cube() → "Leg1"
4. set_scale("Leg1", [0.1, 0.1, 0.8])  # Guess leg size
5. set_location("Leg1", [0.9, 0.4, -0.45])  # Guess position

❌ Résultat: Legs pas alignés, proportions bizarres, pas réaliste
```

**Avec vision:**
```
User: "Crée une table réaliste"

Claude (avec vision):
1. create_cube() → "Table top"
2. set_scale("Table top", [2, 1, 0.1])
3. get_viewport_render() → Voir le plateau
4. "Plateau trop fin, ajustons"
5. set_scale("Table top", [2, 1, 0.05])
6. create_cube() → "Leg1"
7. get_viewport_render() → Voir leg + plateau
8. "Leg trop gros, ajustons"
9. Iterate jusqu'à proportion parfaite

✅ Résultat: Table bien proportionnée, réaliste
```

---

## 🏗️ Architecture de Vision - 3 Niveaux

### Niveau 1: VISION STATIQUE (v0.8) ⭐⭐⭐
**Priority: CRITICAL**

#### Capacités
- Capture viewport screenshot (PNG/JPEG)
- Rendu preview basse résolution
- Multiple angles de vue

#### Outils Nécessaires
```python
# 1. Screenshot viewport
get_viewport_screenshot(
    camera_angle: str = "current",  # "current", "front", "top", "side"
    resolution: tuple = (512, 512),
    format: str = "PNG"
) -> bytes  # Image data

# 2. Quick render preview
render_preview(
    samples: int = 32,  # Low for speed
    resolution: tuple = (512, 512),
    denoising: bool = True
) -> bytes

# 3. Set viewport camera
set_viewport_camera(
    location: List[float],
    look_at_target: str,  # Object name or [x,y,z]
    lens: float = 50.0
) -> dict
```

#### Architecture Technique
```
Claude Request
    ↓
MCP Server: tools/call "get_viewport_screenshot"
    ↓
Bridge: Capture viewport
    ↓
Blender: bpy.ops.render.opengl(write_still=True)
    ↓
Bridge: Read PNG, base64 encode
    ↓
MCP Server: Return {"image": "base64_data", "size": [512, 512]}
    ↓
Claude: Receives image, analyzes with vision
    ↓
Claude: "The leg is too thick, let me adjust..."
```

#### Implémentation Priority
```python
# HIGH PRIORITY - Add to v0.8
def get_viewport_screenshot(params):
    """Capture current viewport as image"""
    import tempfile
    import base64

    # Set resolution
    bpy.context.scene.render.resolution_x = params.get("width", 512)
    bpy.context.scene.render.resolution_y = params.get("height", 512)

    # Set camera if specified
    angle = params.get("camera_angle", "current")
    if angle != "current":
        _set_viewport_angle(angle)

    # Render to temp file
    temp_path = tempfile.mktemp(suffix=".png")
    bpy.ops.render.opengl(write_still=True)
    bpy.data.images['Render Result'].save_render(temp_path)

    # Read and encode
    with open(temp_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    os.unlink(temp_path)

    return {
        "image_base64": image_data,
        "width": 512,
        "height": 512,
        "format": "PNG"
    }
```

#### Use Cases
- ✅ Check proportions after scaling
- ✅ Verify alignment after positioning
- ✅ Review material appearance
- ✅ Detect intersections/collisions
- ✅ Validate scene composition

---

### Niveau 2: VISION INTERACTIVE (v1.0) ⭐⭐
**Priority: HIGH**

#### Capacités
- Streaming viewport updates
- Real-time feedback loop
- Multiple viewport angles simultanés
- Measurement overlays

#### Outils Nécessaires
```python
# 1. Start viewport stream (WebSocket)
start_viewport_stream(
    fps: int = 2,  # Updates per second
    resolution: tuple = (256, 256),
    angles: List[str] = ["perspective", "top"]
) -> str  # Stream ID

# 2. Get measurement overlay
get_measurements(
    objects: List[str],
    show_dimensions: bool = True,
    show_distances: bool = True
) -> dict  # Annotated image

# 3. Visual diff
compare_viewports(
    before_image: str,  # base64
    after_image: str
) -> dict  # Highlighted differences
```

#### Architecture
```
WebSocket Server in Bridge
    ↓
Continuous viewport capture (2 FPS)
    ↓
Compress & stream to MCP
    ↓
Claude analyzes stream
    ↓
Real-time adjustments
```

#### Use Cases
- ✅ Live modeling feedback
- ✅ Animation preview
- ✅ Interactive adjustments
- ✅ Multi-angle validation

---

### Niveau 3: VISION COGNITIVE (v1.5+) ⭐
**Priority: MEDIUM (Research)**

#### Capacités
- Scene understanding (semantic segmentation)
- Object detection & classification
- Spatial reasoning from images
- Style/aesthetic evaluation

#### Outils Nécessaires
```python
# 1. Scene analysis
analyze_scene_composition(
    viewport_image: bytes
) -> dict  # {objects: [...], composition_score, suggestions}

# 2. Detect modeling errors
detect_mesh_issues(
    object_name: str,
    viewport_image: bytes
) -> dict  # {non_manifold, holes, overlaps}

# 3. Style matching
match_reference_style(
    current_scene: bytes,
    reference_image: bytes
) -> dict  # {similarity_score, differences, suggestions}
```

#### Research Areas
- Computer vision integration
- Style transfer for 3D
- Procedural generation guided by vision
- AI-assisted mesh optimization

---

## 🧠 Cognition Spatiale - Understanding 3D Space

### Problème Actuel
Claude comprend les coordonnées [x, y, z] mais pas **l'espace 3D réel**.

#### Ce qui manque:
- Notion de "devant/derrière"
- Compréhension des distances relatives
- Sens des proportions réalistes
- Conscience des occlusions

### Solutions

#### 1. Spatial Context Tools (v0.8)
```python
# Get spatial relationships
get_spatial_relationships(
    object_name: str
) -> dict:
    return {
        "position": [x, y, z],
        "nearest_objects": [
            {"name": "Cube", "distance": 2.5, "direction": "above"},
            {"name": "Light", "distance": 5.0, "direction": "front-left"}
        ],
        "bounding_box": {
            "min": [x1, y1, z1],
            "max": [x2, y2, z2],
            "size": [w, h, d]
        },
        "in_camera_view": True
    }
```

#### 2. Scene Graph (v0.9)
```python
# Get hierarchical scene structure
get_scene_graph() -> dict:
    return {
        "scene": "Scene",
        "objects": [
            {
                "name": "Table",
                "type": "MESH",
                "children": [
                    {"name": "TableTop", "parent": "Table"},
                    {"name": "Leg1", "parent": "Table"},
                    {"name": "Leg2", "parent": "Table"}
                ],
                "spatial_group": "Furniture"
            }
        ]
    }
```

#### 3. Measurement Tools (v0.8)
```python
# Measure distances
measure_distance(
    from_object: str,
    to_object: str
) -> float

# Check if objects intersect
check_intersection(
    object1: str,
    object2: str
) -> dict  # {intersecting: bool, overlap_volume: float}

# Get real-world scale
get_real_world_dimensions(
    object_name: str,
    unit: str = "meters"
) -> dict  # {width: 2.0, height: 0.8, depth: 1.0}
```

---

## ✋ Manipulation Précise - Fine Control

### Niveau 1: Transform Control (v0.7) ✅
**Status: In Progress**

```python
# Already have:
- set_location()
- set_rotation_euler()  # Adding this week
- set_scale()  # Adding this week

# Need to add:
- move_relative()  # Move by delta
- rotate_relative()  # Rotate by delta
- scale_relative()  # Scale by factor
```

### Niveau 2: Vertex-Level Control (v0.9)
**Priority: HIGH for serious modeling**

```python
# Edit mode operations
enter_edit_mode(object_name: str)
exit_edit_mode()

# Vertex operations
get_vertices(object_name: str) -> List[dict]
select_vertices(indices: List[int])
move_vertices(indices: List[int], delta: List[float])
delete_vertices(indices: List[int])

# Edge operations
add_edge(vertex1: int, vertex2: int)
subdivide_edge(edge_index: int, cuts: int = 1)

# Face operations
add_face(vertices: List[int])
extrude_face(face_index: int, distance: float)
inset_face(face_index: int, thickness: float)
```

### Niveau 3: Modifier Stack (v1.0)
**Priority: MEDIUM**

```python
# Common modifiers
add_subdivision_surface(object_name: str, levels: int = 2)
add_mirror_modifier(object_name: str, axis: str = "X")
add_array_modifier(object_name: str, count: int, offset: List[float])
add_bevel_modifier(object_name: str, width: float)

# Apply modifiers
apply_modifier(object_name: str, modifier_name: str)
apply_all_modifiers(object_name: str)
```

---

## 🎨 Complete Workflow Example (v1.0 Target)

**Task: "Create a realistic wooden chair"**

### Step 1: Planning (with spatial cognition)
```python
# Claude thinks:
"A chair needs:
- Seat (40cm x 40cm x 5cm)
- Back (40cm x 50cm x 3cm)
- 4 Legs (5cm x 5cm x 45cm each)
- Proportions: seat height ~45cm"
```

### Step 2: Initial Creation
```python
1. create_cube() → "Seat"
2. set_scale("Seat", [0.4, 0.4, 0.05])
3. set_location("Seat", [0, 0, 0.45])

# VISION CHECK
4. viewport_screenshot = get_viewport_screenshot(angle="perspective")
5. Claude analyzes: "Seat looks good, proportions correct"
```

### Step 3: Add Components
```python
6. create_cube() → "Back"
7. set_scale("Back", [0.4, 0.03, 0.5])
8. set_location("Back", [0, 0.2, 0.7])

# VISION CHECK
9. viewport_screenshot = get_viewport_screenshot(angle="side")
10. Claude: "Back angle needs adjustment"
11. set_rotation_euler("Back", [10, 0, 0])  # Slight tilt

# SPATIAL CHECK
12. relationships = get_spatial_relationships("Back")
13. Claude: "Distance from seat correct: 0.25m"
```

### Step 4: Add Legs
```python
# Create one leg, position, then duplicate
14. create_cube() → "Leg1"
15. set_scale("Leg1", [0.05, 0.05, 0.45])
16. set_location("Leg1", [0.175, 0.175, 0.225])

# VISION CHECK - Multi angle
17. front_view = get_viewport_screenshot(angle="front")
18. top_view = get_viewport_screenshot(angle="top")
19. Claude: "Leg position looks good"

# Duplicate with measurements
20. distances = measure_distance("Leg1", "Seat")
21. duplicate_object("Leg1") → "Leg2"
22. set_location("Leg2", [-0.175, 0.175, 0.225])
# ... repeat for Leg3, Leg4
```

### Step 5: Materials & Finish
```python
23. create_material("Wood")
24. set_material_color("Wood", [0.4, 0.25, 0.15, 1.0])  # Brown
25. set_material_roughness("Wood", 0.7)  # Matte wood
26. assign_material("Seat", "Wood")
# ... assign to all parts

# FINAL VISION CHECK - High quality render
27. final_render = render_preview(samples=128, resolution=(1024, 1024))
28. Claude: "Chair looks realistic and well-proportioned!"
```

### Step 6: Validation
```python
29. scene_info = get_scene_graph()
30. measurements = get_real_world_dimensions("Seat", unit="cm")
31. Claude: "Seat is 40cm x 40cm - perfect for human use ✓"
32. intersection_check = check_intersection("Leg1", "Seat")
33. Claude: "No unwanted intersections ✓"
```

---

## 🏆 Tool Priority Matrix

### Immediate (v0.7-0.8) - THIS WEEK
1. ⭐⭐⭐ **get_viewport_screenshot** - CRITICAL
2. ⭐⭐⭐ **get_spatial_relationships** - CRITICAL
3. ⭐⭐⭐ **measure_distance** - HIGH
4. ⭐⭐ **check_intersection** - HIGH
5. ⭐⭐ **render_preview** - HIGH

### Short-term (v0.9) - 2-3 WEEKS
6. ⭐⭐⭐ **Vertex editing** - Edit mode operations
7. ⭐⭐ **Scene graph** - Hierarchical relationships
8. ⭐⭐ **Bounding boxes** - Spatial awareness
9. ⭐ **Viewport angles** - Multiple views

### Medium-term (v1.0) - 1-2 MONTHS
10. ⭐⭐ **Modifier stack** - Non-destructive editing
11. ⭐⭐ **Viewport streaming** - Real-time feedback
12. ⭐ **Scene analysis** - AI-assisted composition
13. ⭐ **Style matching** - Reference-based modeling

---

## 🎯 Success Metrics

### Vision System Success
- ✅ Claude can verify results visually
- ✅ Iterative refinement based on appearance
- ✅ No "blind guessing" of dimensions
- ✅ Proportions match real-world expectations

### Spatial Cognition Success
- ✅ Understands object relationships
- ✅ Measures distances accurately
- ✅ Detects collisions/intersections
- ✅ Maintains realistic scale

### Manipulation Success
- ✅ Precise vertex-level control
- ✅ Non-destructive editing (modifiers)
- ✅ Batch operations for efficiency
- ✅ Undo/redo support

---

## 🚀 Implementation Strategy

### Week 1 (v0.7)
- [ ] Implement rotation & scale tools
- [ ] Add material system
- [ ] **START**: Viewport screenshot prototype

### Week 2 (v0.8)
- [ ] **SHIP**: get_viewport_screenshot
- [ ] **SHIP**: get_spatial_relationships
- [ ] **SHIP**: measure_distance
- [ ] Demo: "Claude creates table with vision feedback"

### Week 3-4 (v0.9)
- [ ] Vertex editing tools
- [ ] Scene graph
- [ ] Multiple viewport angles
- [ ] Demo: "Claude models chair from description"

### Month 2 (v1.0)
- [ ] Modifier stack
- [ ] Viewport streaming
- [ ] Advanced rendering
- [ ] Public launch with vision capabilities

---

## 🤔 Technical Challenges

### Challenge 1: Image Size
**Problem:** Base64 images can be large (512x512 PNG ~300KB)
**Solutions:**
- JPEG with 80% quality (smaller)
- Adaptive resolution (256x256 for quick checks)
- Compression in bridge before sending
- Streaming for large images

### Challenge 2: Vision Latency
**Problem:** Screenshot + analyze + adjust = slow loop
**Solutions:**
- Async screenshot capture (non-blocking)
- Cache viewport state to avoid redundant captures
- Low-res quick previews, high-res final
- Batch multiple checks in one request

### Challenge 3: 3D → 2D Ambiguity
**Problem:** Single viewport can't show all spatial relationships
**Solutions:**
- Multiple camera angles in single response
- Depth buffer alongside color image
- Wireframe overlay option
- Measurement annotations on image

### Challenge 4: Context Window
**Problem:** Images consume Claude's context
**Solutions:**
- Compress images aggressively
- Only send images when needed
- Clear old images from context
- Summarize visual state in text

---

## 💡 Innovation Opportunities

### AI-Assisted Modeling
```python
# Claude generates mesh from description
generate_mesh_from_description(
    description: str,
    reference_images: List[bytes] = None
) -> str  # Object name
```

### Procedural Workflows
```python
# Chain operations with vision validation
modeling_workflow = [
    {"action": "create_cube", "params": {}},
    {"action": "get_screenshot", "validate": "check proportions"},
    {"action": "adjust_if_needed", "criteria": "realistic"},
    {"action": "repeat_until", "condition": "visually_acceptable"}
]
```

### Multi-Modal Learning
- Learn from user corrections
- Build library of "good proportions"
- Style consistency across projects
- Pattern recognition for common objects

---

## 📊 Comparison: Human vs Claude (v1.0)

| Capability | Human Artist | Claude (v0.4) | Claude (v1.0 Target) |
|------------|--------------|---------------|----------------------|
| **Vision** | ✅ Real-time | ❌ Blind | ✅ Screenshots + streaming |
| **Spatial Awareness** | ✅ Intuitive | ⚠️ Coordinates only | ✅ Relationships + measurements |
| **Proportions** | ✅ Experience-based | ❌ Guesses | ✅ Vision-verified |
| **Iteration Speed** | ⚠️ Manual | ✅ Fast tools | ✅ Vision-guided |
| **Precision** | ⚠️ Approximate | ✅ Exact math | ✅ Best of both |
| **Creativity** | ✅ High | ✅ Very high | ✅ Very high |
| **Consistency** | ⚠️ Varies | ✅ Perfect | ✅ Perfect |

---

## 🎯 Conclusion

Pour que Claude modélise comme un pro, il faut:

1. **👀 VISION (v0.8)** - CRITIQUE
   - Viewport screenshots
   - Render previews
   - Multiple angles

2. **🧠 COGNITION (v0.9)** - IMPORTANT
   - Spatial relationships
   - Measurements
   - Scene graph

3. **✋ MANIPULATION (v0.7-1.0)** - PROGRESSIF
   - Transform tools (v0.7) ✓
   - Vertex editing (v0.9)
   - Modifiers (v1.0)

**Priority Order:**
1. Ship transform tools (rotation, scale) - THIS WEEK
2. Add viewport screenshots - NEXT WEEK
3. Add spatial relationships - NEXT WEEK
4. Everything else follows

**The game-changer is VISION.** Sans ça, Claude reste aveugle. Avec ça, il devient artiste.
