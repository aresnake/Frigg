"""
Prototype Bridge Functions for Frigg MCP

Copy these functions into frigg_blender_bridge.py to test new tools.
Once tested and working, they can be officially integrated.

Usage:
1. Copy desired functions into frigg_blender_bridge.py
2. Add handler in handle_request()
3. Test with prototype_tools.py
4. If working, add to MCP server stdio.py
"""

import bpy
import math
import base64
import tempfile
import os
from mathutils import Vector


# ============================================================================
# VISION TOOLS
# ============================================================================

def get_viewport_screenshot(params):
    """
    Capture current viewport as image

    Tool: frigg.blender.get_viewport_screenshot
    Priority: CRITICAL for v0.8
    """
    width = params.get("width", 512)
    height = params.get("height", 512)
    angle = params.get("angle", "perspective")

    # Set render resolution
    scene = bpy.context.scene
    original_x = scene.render.resolution_x
    original_y = scene.render.resolution_y

    scene.render.resolution_x = width
    scene.render.resolution_y = height

    # Set viewport angle if specified
    if angle in ["front", "back", "left", "right", "top", "bottom"]:
        # Store original view
        area = None
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    break

        if area:
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {
                        'window': window,
                        'screen': window.screen,
                        'area': area,
                        'region': region,
                    }
                    # Set view angle
                    if angle == "front":
                        bpy.ops.view3d.view_axis(override, type='FRONT')
                    elif angle == "top":
                        bpy.ops.view3d.view_axis(override, type='TOP')
                    elif angle == "right":
                        bpy.ops.view3d.view_axis(override, type='RIGHT')
                    # Add more as needed

    # Render viewport
    temp_path = tempfile.mktemp(suffix=".png")
    try:
        # Use OpenGL render for speed
        bpy.ops.render.opengl(write_still=True)
        bpy.data.images['Render Result'].save_render(temp_path)

        # Read and encode image
        with open(temp_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Cleanup
        os.unlink(temp_path)

        # Restore resolution
        scene.render.resolution_x = original_x
        scene.render.resolution_y = original_y

        return {
            "image_base64": image_data,
            "width": width,
            "height": height,
            "format": "PNG",
            "angle": angle
        }

    except Exception as e:
        # Restore resolution on error
        scene.render.resolution_x = original_x
        scene.render.resolution_y = original_y
        raise RuntimeError(f"Failed to capture viewport: {e}")


def render_preview(params):
    """
    Quick render preview with low samples

    Tool: frigg.blender.render_preview
    Priority: HIGH for v0.8
    """
    import time

    samples = params.get("samples", 32)
    width = params.get("width", 512)
    height = params.get("height", 512)

    scene = bpy.context.scene

    # Store original settings
    original_samples = scene.cycles.samples
    original_x = scene.render.resolution_x
    original_y = scene.render.resolution_y

    # Set preview settings
    scene.cycles.samples = samples
    scene.render.resolution_x = width
    scene.render.resolution_y = height

    temp_path = tempfile.mktemp(suffix=".png")

    try:
        start_time = time.time()

        # Render
        scene.render.filepath = temp_path
        bpy.ops.render.render(write_still=True)

        render_time = time.time() - start_time

        # Read and encode
        with open(temp_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        os.unlink(temp_path)

        # Restore settings
        scene.cycles.samples = original_samples
        scene.render.resolution_x = original_x
        scene.render.resolution_y = original_y

        return {
            "image_base64": image_data,
            "width": width,
            "height": height,
            "samples": samples,
            "render_time": round(render_time, 2)
        }

    except Exception as e:
        # Restore settings on error
        scene.cycles.samples = original_samples
        scene.render.resolution_x = original_x
        scene.render.resolution_y = original_y
        raise RuntimeError(f"Render failed: {e}")


# ============================================================================
# SPATIAL COGNITION TOOLS
# ============================================================================

def measure_distance(params):
    """
    Measure distance between two objects

    Tool: frigg.blender.measure_distance
    Priority: CRITICAL for v0.8
    """
    obj1_name = params.get("object1")
    obj2_name = params.get("object2")

    if not obj1_name or not obj2_name:
        raise ValueError("measure_distance requires object1 and object2")

    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)

    if not obj1:
        raise ValueError(f"Object not found: {obj1_name}")
    if not obj2:
        raise ValueError(f"Object not found: {obj2_name}")

    # Calculate distance between origins
    distance = (obj1.location - obj2.location).length

    return {
        "object1": obj1_name,
        "object2": obj2_name,
        "distance": float(distance),
        "world_distance": {
            "blender_units": float(distance),
            "meters": float(distance),  # Assuming 1 BU = 1m
            "centimeters": float(distance * 100),
            "inches": float(distance * 39.3701)
        },
        "vector": [
            float(obj2.location.x - obj1.location.x),
            float(obj2.location.y - obj1.location.y),
            float(obj2.location.z - obj1.location.z)
        ]
    }


def get_spatial_relationships(params):
    """
    Get spatial relationships for an object

    Tool: frigg.blender.get_spatial_relationships
    Priority: CRITICAL for v0.8
    """
    obj_name = params.get("object_name")
    if not obj_name:
        raise ValueError("get_spatial_relationships requires object_name")

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError(f"Object not found: {obj_name}")

    # Get bounding box
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bbox_min = Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox)))
    bbox_max = Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
    dimensions = bbox_max - bbox_min

    # Find nearest objects
    nearest = []
    for other in bpy.data.objects:
        if other.name == obj_name:
            continue

        distance = (obj.location - other.location).length
        if distance < 100:  # Only include objects within 100 units
            # Determine direction
            delta = other.location - obj.location
            if abs(delta.z) > abs(delta.x) and abs(delta.z) > abs(delta.y):
                direction = "above" if delta.z > 0 else "below"
            elif abs(delta.y) > abs(delta.x):
                direction = "front" if delta.y > 0 else "behind"
            else:
                direction = "right" if delta.x > 0 else "left"

            nearest.append({
                "name": other.name,
                "distance": float(distance),
                "direction": direction,
                "type": other.type
            })

    # Sort by distance
    nearest.sort(key=lambda x: x["distance"])

    # Check if in camera view (if camera exists)
    in_camera_view = False
    camera = bpy.context.scene.camera
    if camera:
        # Simple check: is object in front of camera
        camera_to_obj = obj.location - camera.location
        camera_forward = camera.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        in_camera_view = camera_to_obj.dot(camera_forward) > 0

    return {
        "name": obj_name,
        "location": [float(v) for v in obj.location],
        "rotation_euler": [float(v) for v in obj.rotation_euler],
        "scale": [float(v) for v in obj.scale],
        "dimensions": [float(v) for v in dimensions],
        "bounding_box": {
            "min": [float(v) for v in bbox_min],
            "max": [float(v) for v in bbox_max]
        },
        "nearest_objects": nearest[:10],  # Top 10 nearest
        "in_camera_view": in_camera_view,
        "type": obj.type,
        "parent": obj.parent.name if obj.parent else None,
        "children": [child.name for child in obj.children]
    }


def check_intersection(params):
    """
    Check if two objects intersect (bounding box check)

    Tool: frigg.blender.check_intersection
    Priority: MEDIUM for v0.8
    """
    obj1_name = params.get("object1")
    obj2_name = params.get("object2")

    if not obj1_name or not obj2_name:
        raise ValueError("check_intersection requires object1 and object2")

    obj1 = bpy.data.objects.get(obj1_name)
    obj2 = bpy.data.objects.get(obj2_name)

    if not obj1:
        raise ValueError(f"Object not found: {obj1_name}")
    if not obj2:
        raise ValueError(f"Object not found: {obj2_name}")

    # Get bounding boxes
    def get_bbox(obj):
        bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        return (
            Vector((min(v.x for v in bbox), min(v.y for v in bbox), min(v.z for v in bbox))),
            Vector((max(v.x for v in bbox), max(v.y for v in bbox), max(v.z for v in bbox)))
        )

    bbox1_min, bbox1_max = get_bbox(obj1)
    bbox2_min, bbox2_max = get_bbox(obj2)

    # Check AABB intersection
    intersecting = (
        bbox1_min.x <= bbox2_max.x and bbox1_max.x >= bbox2_min.x and
        bbox1_min.y <= bbox2_max.y and bbox1_max.y >= bbox2_min.y and
        bbox1_min.z <= bbox2_max.z and bbox1_max.z >= bbox2_min.z
    )

    result = {
        "object1": obj1_name,
        "object2": obj2_name,
        "intersecting": intersecting
    }

    if intersecting:
        # Calculate overlap volume (approximate)
        overlap_x = min(bbox1_max.x, bbox2_max.x) - max(bbox1_min.x, bbox2_min.x)
        overlap_y = min(bbox1_max.y, bbox2_max.y) - max(bbox1_min.y, bbox2_min.y)
        overlap_z = min(bbox1_max.z, bbox2_max.z) - max(bbox1_min.z, bbox2_min.z)
        result["overlap_volume"] = float(overlap_x * overlap_y * overlap_z)
    else:
        # Calculate minimum distance
        distance = (obj1.location - obj2.location).length
        result["min_distance"] = float(distance)

    return result


def get_scene_graph(params):
    """
    Get hierarchical scene structure

    Tool: frigg.blender.get_scene_graph
    Priority: MEDIUM for v0.9
    """
    def build_object_tree(obj):
        """Recursively build object tree"""
        return {
            "name": obj.name,
            "type": obj.type,
            "location": [float(v) for v in obj.location],
            "visible": not obj.hide_viewport,
            "children": [build_object_tree(child) for child in obj.children]
        }

    # Get root objects (objects without parents)
    root_objects = [obj for obj in bpy.data.objects if obj.parent is None]

    # Build tree
    object_trees = [build_object_tree(obj) for obj in root_objects]

    # Get collections info
    collections = []
    for coll in bpy.data.collections:
        collections.append({
            "name": coll.name,
            "objects": [obj.name for obj in coll.objects],
            "visible": not coll.hide_viewport
        })

    return {
        "scene_name": bpy.context.scene.name,
        "total_objects": len(bpy.data.objects),
        "objects": object_trees,
        "collections": collections,
        "active_object": bpy.context.active_object.name if bpy.context.active_object else None
    }


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

"""
To integrate these functions into frigg_blender_bridge.py:

1. Copy the functions you want to test

2. Add handlers in handle_request():

    if method == "get_viewport_screenshot":
        return {"result": get_viewport_screenshot(params)}

    if method == "measure_distance":
        return {"result": measure_distance(params)}

    if method == "get_spatial_relationships":
        return {"result": get_spatial_relationships(params)}

    if method == "check_intersection":
        return {"result": check_intersection(params)}

    if method == "render_preview":
        return {"result": render_preview(params)}

    if method == "get_scene_graph":
        return {"result": get_scene_graph(params)}

3. Test with:
   python tools/prototype_tools.py <tool_name>

4. Once working, add to stdio.py as official MCP tools
"""
