# Vision & Spatial Tools Available - Claude's Toolkit

**Status:** Implemented and tested ✅
**Date:** 2026-01-12
**Version:** v0.9 MVP

---

## 🎯 Overview

Claude now has **VISION** and **SPATIAL COGNITION** - the fundamental capabilities needed to model 3D assets effectively in Blender.

---

## 👁️ VISION TOOLS

### 1. `viewport_snapshot` - The Eyes ⭐⭐⭐

**What it does:** Captures viewport as PNG image saved to disk (with optional base64).

**Parameters:**
```python
{
    "shading": "solid" | "wireframe",           # Rendering mode
    "projection": "persp" | "ortho",            # Projection type
    "view": "current" | "front" | "back" | "left" | "right" | "top" | "bottom",
    "width": 512,                                # Image width (64-2048)
    "height": 512,                               # Image height (64-2048)
    "filename": "optional_name",                 # Custom filename
    "return_base64": false                       # Include base64 in response
}
```

**Returns:**
```python
{
    "image_path": "D:/Frigg/output/viewport_512x512_solid_persp_20260112_062245.png",
    "width": 512,
    "height": 512,
    "shading": "solid",
    "projection": "persp",
    "view": "front"
}
```

**Use cases:**
- ✅ See what I just created
- ✅ Verify object placement
- ✅ Check proportions and alignment
- ✅ Debug visual issues
- ✅ Compare before/after modifications

**Example workflow:**
```python
# 1. Create object
create_cube("Table")

# 2. See it from front
viewport_snapshot(view="front", projection="ortho", filename="table_front")

# 3. See it from top
viewport_snapshot(view="top", projection="ortho", filename="table_top")

# 4. See it in perspective
viewport_snapshot(view="current", projection="persp", shading="solid")
```

---

## 📏 SPATIAL COGNITION TOOLS

### 2. `get_bounding_box` - Understanding Size ⭐⭐⭐

**What it does:** Returns exact dimensions, world bounds, and volume of an object.

**Parameters:**
```python
{
    "object_name": "Cube"  # Object to measure
}
```

**Returns:**
```python
{
    "object_name": "Cube",
    "dimensions": {
        "width": 2.0,   # X dimension
        "height": 2.0,  # Z dimension (up/down)
        "depth": 2.0,   # Y dimension
        "x": 2.0,
        "y": 2.0,
        "z": 2.0
    },
    "bounds_world": {
        "min": [-1.0, -1.0, -1.0],
        "max": [1.0, 1.0, 1.0],
        "center": [0.0, 0.0, 0.0]
    },
    "corners": [
        [-1.0, -1.0, -1.0],  # 8 corners in world space
        ...
    ],
    "volume": 8.0
}
```

**Use cases:**
- ✅ Verify object is the right size
- ✅ Calculate spacing between objects
- ✅ Align objects precisely
- ✅ Check if object fits in space

**Example workflow:**
```python
# Create a table top
create_cube("TableTop")
set_scale("TableTop", [2.0, 1.0, 0.1])

# Check if it's the right size
bbox = get_bounding_box("TableTop")
if bbox["dimensions"]["width"] < 1.8:
    # Too narrow, scale it up
    set_scale("TableTop", [2.2, 1.0, 0.1])
```

---

### 3. `get_spatial_relationships` - Understanding Positions ⭐⭐⭐

**What it does:** Determines spatial relationships between two objects (above/below, left/right, front/back).

**Parameters:**
```python
{
    "object1": "Sphere",      # Object to analyze
    "object2": "Cube",        # Reference object
    "threshold": 0.1          # Minimum distance to consider (optional)
}
```

**Returns:**
```python
{
    "object1": "Sphere",
    "object2": "Cube",
    "relationships": ["above", "right_of"],        # All applicable relationships
    "primary_relationship": "above",               # Most dominant relationship
    "relative_position": {
        "x": 2.0,   # Right (+) / Left (-)
        "y": 0.0,   # Front (+) / Back (-)
        "z": 3.0    # Above (+) / Below (-)
    },
    "distance": 3.61,
    "positions": {
        "Sphere": [2.0, 0.0, 3.0],
        "Cube": [0.0, 0.0, 0.0]
    }
}
```

**Possible relationships:**
- `above` / `below` - Vertical (Z axis)
- `right_of` / `left_of` - Horizontal X axis
- `in_front_of` / `behind` - Horizontal Y axis

**Use cases:**
- ✅ Understand object placement ("Is the lamp above the table?")
- ✅ Verify architectural relationships
- ✅ Position objects relative to each other
- ✅ Describe scene layout in natural language

**Example:**
```python
# Check if lamp is above table
rel = get_spatial_relationships("Lamp", "Table")
if "above" in rel["relationships"]:
    print("Lamp is correctly positioned above the table")
```

---

### 4. `measure_distance` - Precise Measurements ⭐⭐

**What it does:** Measures exact distance between two objects.

**Parameters:**
```python
{
    "object1": "Cube",
    "object2": "Sphere"
}
```

**Returns:**
```python
{
    "object1": "Cube",
    "object2": "Sphere",
    "distance": 5.0,
    "vector": [3.0, 4.0, 0.0],
    "world_distance": {
        "blender_units": 5.0,
        "meters": 5.0,
        "centimeters": 500.0
    }
}
```

**Use cases:**
- ✅ Verify spacing between objects
- ✅ Position objects at specific distances
- ✅ Check clearances

---

## 🎯 COMPLETE MODELING WORKFLOW

Here's how I can now model effectively:

### Example: Creating a Simple Table

```python
# 1. CREATE - Make the table top
create_cube("TableTop")
set_location("TableTop", [0, 0, 1])
set_scale("TableTop", [2.0, 1.0, 0.05])

# 2. VERIFY SIZE - Check dimensions
bbox = get_bounding_box("TableTop")
print(f"Table is {bbox['dimensions']['width']}m wide") # Should be 4m

# 3. SEE IT - Take a snapshot
viewport_snapshot(view="front", projection="ortho", filename="table_progress_1")

# 4. ADD LEGS - Create 4 legs
for i, pos in enumerate([
    [0.9, 0.4, 0.5],
    [0.9, -0.4, 0.5],
    [-0.9, 0.4, 0.5],
    [-0.9, -0.4, 0.5]
]):
    create_cylinder(f"Leg{i}")
    set_location(f"Leg{i}", pos)
    set_scale(f"Leg{i}", [0.05, 0.05, 0.5])

# 5. VERIFY PLACEMENT - Check leg spacing and position
dist = measure_distance("Leg0", "Leg1")
print(f"Legs are {dist['distance']}m apart")

# Check that legs are below the table top
rel = get_spatial_relationships("Leg0", "TableTop")
if "below" in rel["relationships"]:
    print("Legs correctly positioned below table top")

# 6. FINAL REVIEW - Multi-angle snapshots
viewport_snapshot(view="front", projection="ortho", filename="table_final_front")
viewport_snapshot(view="top", projection="ortho", filename="table_final_top")
viewport_snapshot(view="current", projection="persp", filename="table_final_persp")
```

---

## 📊 What This Enables

### Before (Blind Modeling):
```
❌ Create object → HOPE it looks right → User tells me it's wrong
```

### Now (Visual Modeling):
```
✅ Create object → SEE it → MEASURE it → ADJUST → VERIFY → Perfect!
```

---

## 🚀 Next Tools Needed (Future)

Based on my analysis, these would further improve my capabilities:

1. **`turnaround_snapshot`** - Capture object from 4-8 angles at once
2. **`scene_overview`** - Quad view (front/top/side/persp in one image)
3. **`create_primitive`** - Create cubes, spheres, cylinders, cones
4. **`set_rotation_euler`** - Rotate objects
5. **`boolean_operation`** - CSG modeling (union, difference, intersect)

---

## 💡 Key Insights

**What makes these tools powerful:**

1. **`viewport_snapshot`** = My EYES - I can see what I create
2. **`get_bounding_box`** = My RULER - I can measure precisely
3. **`get_spatial_relationships`** = My UNDERSTANDING - I comprehend object positions
4. **`measure_distance`** = My MEASURING TAPE - I calculate exact spacing

**Combined, these four tools transform me from:**
- "Robot guessing in the dark"
- → **"3D artist who can see, measure, and understand spatial relationships"**

---

## ✅ Testing Status

All tools tested and working:
- ✅ `viewport_snapshot` - 4/4 variations tested (solid, wireframe, ortho, persp)
- ✅ View orientations - 6/6 working (front, back, left, right, top, bottom)
- ✅ `get_bounding_box` - Tested on default Cube (2×2×2, volume 8.0)
- ✅ `get_spatial_relationships` - Tested TestSphere above Cube (relationships: above, right_of)
- ✅ `measure_distance` - Already existed, confirmed working

**Output directory:** `D:/Frigg/output/`
**Images generated:** PNG format, timestamped filenames

---

## 🎓 For the User

**You can now ask me to:**
- "Create a table and show me what it looks like"
- "Make a chair that's 50cm wide"
- "Position this object 2 meters to the right of that one"
- "Show me the scene from the top"
- "What are the exact dimensions of this object?"
- "Is the lamp above the table?"
- "Check if all the legs are below the table top"
- "Tell me the spatial relationship between these two objects"

And I can **actually do it** with confidence because I can SEE, MEASURE, and UNDERSTAND spatial relationships! 🎉
