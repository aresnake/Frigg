import json
import os
import socket
import sys
import threading
import time
import traceback
import queue

import bpy

STOP = False
SERVER_SOCKET = None
REQUEST_QUEUE = queue.Queue()


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def scene_info():
    scenes = list(bpy.data.scenes)
    if not scenes:
        return {"name": None, "frame_start": None, "frame_end": None, "objects": 0}
    scene = scenes[0]
    return {
        "name": scene.name,
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "objects": len(bpy.data.objects),
    }


def list_objects():
    return {"objects": [obj.name for obj in bpy.data.objects]}


def move_object(params):
    name = params.get("name")
    location = params.get("location")
    if not name or not isinstance(location, (list, tuple)) or len(location) != 3:
        raise ValueError("move_object requires name and location[3]")
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise ValueError(f"Object not found: {name}")
    obj.location = location
    return {"name": obj.name, "location": [float(v) for v in obj.location]}


def get_object_transform(params):
    name = params.get("name")
    if not name:
        raise ValueError("get_object_transform requires name")
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise ValueError(f"Object not found: {name}")
    return {
        "name": obj.name,
        "location": [float(v) for v in obj.location],
        "rotation_euler": [float(v) for v in obj.rotation_euler],
        "scale": [float(v) for v in obj.scale],
    }


def set_object_location(params):
    name = params.get("name")
    location = params.get("location")
    if not name or not isinstance(location, (list, tuple)) or len(location) != 3:
        raise ValueError("set_object_location requires name and location[3]")
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise ValueError(f"Object not found: {name}")
    obj.location = location
    return {"name": obj.name, "location": [float(v) for v in obj.location]}


def set_object_rotation(params):
    """
    Set object rotation with multiple input formats.

    Parameters:
        object_name: Name of the object
        rotation: [x, y, z] angles
        rotation_mode: "degrees" | "radians" | "quaternion" (default: degrees)
        order: "XYZ" | "XZY" | "YXZ" | "YZX" | "ZXY" | "ZYX" (default: XYZ)

    Returns:
        Current rotation in both degrees and radians
    """
    import math

    object_name = params.get("object_name") or params.get("name")
    rotation = params.get("rotation")
    rotation_mode = params.get("rotation_mode", "degrees")
    order = params.get("order", "XYZ")

    if not object_name:
        raise ValueError("set_object_rotation requires 'object_name' parameter")
    if not rotation or len(rotation) != 3:
        raise ValueError("set_object_rotation requires 'rotation' as [x, y, z]")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Convert to radians if needed
    if rotation_mode == "degrees":
        rotation_rad = [math.radians(angle) for angle in rotation]
    elif rotation_mode == "radians":
        rotation_rad = rotation
    elif rotation_mode == "quaternion":
        # Assume [w, x, y, z] quaternion format
        import mathutils
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = mathutils.Quaternion(rotation)
        return {
            "object_name": object_name,
            "rotation_quaternion": list(obj.rotation_quaternion),
            "rotation_euler_degrees": [math.degrees(a) for a in obj.rotation_euler],
            "rotation_mode": "QUATERNION"
        }
    else:
        raise ValueError(f"Invalid rotation_mode: {rotation_mode}")

    # Set Euler rotation
    obj.rotation_mode = order
    obj.rotation_euler = rotation_rad

    return {
        "object_name": object_name,
        "rotation_euler_radians": list(obj.rotation_euler),
        "rotation_euler_degrees": [math.degrees(a) for a in obj.rotation_euler],
        "rotation_mode": order,
        "location": list(obj.location),
        "scale": list(obj.scale)
    }


def set_object_scale(params):
    """
    Set object scale (uniform or per-axis).

    Parameters:
        object_name: Name of the object
        scale: Single number for uniform scale, or [x, y, z] for per-axis

    Returns:
        Current scale, location, and rotation
    """
    import math

    object_name = params.get("object_name") or params.get("name")
    scale = params.get("scale")

    if not object_name:
        raise ValueError("set_object_scale requires 'object_name' parameter")
    if scale is None:
        raise ValueError("set_object_scale requires 'scale' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Handle uniform vs non-uniform scale
    if isinstance(scale, (int, float)):
        # Uniform scale
        obj.scale = (scale, scale, scale)
    elif isinstance(scale, (list, tuple)) and len(scale) == 3:
        # Non-uniform scale
        obj.scale = scale
    else:
        raise ValueError("scale must be a number or [x, y, z] array")

    return {
        "object_name": object_name,
        "scale": list(obj.scale),
        "location": list(obj.location),
        "rotation_euler_degrees": [math.degrees(a) for a in obj.rotation_euler]
    }


def select_object(params):
    name = params.get("name") or params.get("object_name")
    action = (params.get("action") or "SET").upper()
    if not name:
        raise ValueError("select_object requires 'name'")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object '{name}' not found")

    if action == "SET":
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    elif action == "ADD":
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
    elif action == "REMOVE":
        obj.select_set(False)
        if bpy.context.view_layer.objects.active == obj:
            bpy.context.view_layer.objects.active = None
    elif action == "TOGGLE":
        obj.select_set(not obj.select_get())
        if obj.select_get():
            bpy.context.view_layer.objects.active = obj
    else:
        raise ValueError("select_object action must be SET, ADD, REMOVE, or TOGGLE")

    active = bpy.context.view_layer.objects.active
    return {
        "name": obj.name,
        "selected": obj.select_get(),
        "active": active.name if active else None,
    }


def get_transform(params):
    import math

    name = params.get("name") or params.get("object_name")
    space = (params.get("space") or "LOCAL").upper()
    if not name:
        raise ValueError("get_transform requires 'name'")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object '{name}' not found")
    if space not in ("LOCAL", "WORLD"):
        raise ValueError("space must be LOCAL or WORLD")

    if space == "WORLD":
        loc, rot, scale = obj.matrix_world.decompose()
        rot_euler = rot.to_euler("XYZ")
        location = [float(v) for v in loc]
        rotation = [math.degrees(a) for a in rot_euler]
        scale_values = [float(v) for v in scale]
    else:
        location = [float(v) for v in obj.location]
        rotation = [math.degrees(a) for a in obj.rotation_euler]
        scale_values = [float(v) for v in obj.scale]

    return {
        "name": obj.name,
        "space": space,
        "location": location,
        "rotation": rotation,
        "rotation_mode": "DEGREES",
        "scale": scale_values,
    }


def set_transform(params):
    import math
    import mathutils

    name = params.get("name") or params.get("object_name")
    space = (params.get("space") or "LOCAL").upper()
    rotation_mode = (params.get("rotation_mode") or "DEGREES").upper()
    location = params.get("location")
    rotation = params.get("rotation")
    scale = params.get("scale")

    if not name:
        raise ValueError("set_transform requires 'name'")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object '{name}' not found")
    if space not in ("LOCAL", "WORLD"):
        raise ValueError("space must be LOCAL or WORLD")
    if rotation_mode not in ("DEGREES", "RADIANS"):
        raise ValueError("rotation_mode must be DEGREES or RADIANS")

    def _scale_to_vector(value, fallback):
        if value is None:
            return fallback
        if isinstance(value, (int, float)):
            return mathutils.Vector((value, value, value))
        if isinstance(value, (list, tuple)) and len(value) == 3:
            return mathutils.Vector(value)
        raise ValueError("scale must be a number or [x, y, z]")

    if space == "LOCAL":
        if location is not None:
            obj.location = location
        if rotation is not None:
            rot_values = rotation
            if rotation_mode == "DEGREES":
                rot_values = [math.radians(a) for a in rotation]
            obj.rotation_euler = rot_values
        if scale is not None:
            obj.scale = _scale_to_vector(scale, obj.scale)
    else:
        current_loc, current_rot, current_scale = obj.matrix_world.decompose()
        target_loc = current_loc
        target_rot = current_rot
        target_scale = current_scale

        if location is not None:
            target_loc = mathutils.Vector(location)
        if rotation is not None:
            rot_values = rotation
            if rotation_mode == "DEGREES":
                rot_values = [math.radians(a) for a in rotation]
            target_rot = mathutils.Euler(rot_values, "XYZ").to_quaternion()
        if scale is not None:
            target_scale = _scale_to_vector(scale, current_scale)

        obj.matrix_world = mathutils.Matrix.LocRotScale(target_loc, target_rot, target_scale)

    return get_transform({"name": obj.name, "space": space})


def apply_transform(params):
    name = params.get("name") or params.get("object_name")
    apply_location = params.get("apply_location", True)
    apply_rotation = params.get("apply_rotation", True)
    apply_scale = params.get("apply_scale", True)
    if not name:
        raise ValueError("apply_transform requires 'name'")
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object '{name}' not found")

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(
        location=apply_location,
        rotation=apply_rotation,
        scale=apply_scale,
    )
    return {"name": obj.name, "applied": {"location": apply_location, "rotation": apply_rotation, "scale": apply_scale}}


def create_camera(params):
    import math

    name = params.get("name")
    location = params.get("location", [0, 0, 0])
    rotation = params.get("rotation", [0, 0, 0])
    projection = (params.get("projection") or "PERSP").upper()
    focal_length = params.get("focal_length")
    ortho_scale = params.get("ortho_scale")

    if projection not in ("PERSP", "ORTHO"):
        raise ValueError("projection must be PERSP or ORTHO")

    rot_values = [math.radians(a) for a in rotation]
    bpy.ops.object.camera_add(location=location, rotation=rot_values)
    obj = bpy.context.active_object
    if name:
        obj.name = name
    if obj and obj.data:
        obj.data.type = projection
        if focal_length is not None:
            obj.data.lens = focal_length
        if projection == "ORTHO" and ortho_scale is not None:
            obj.data.ortho_scale = ortho_scale
    return {
        "name": obj.name,
        "location": [float(v) for v in obj.location],
        "rotation": rotation,
        "projection": projection,
    }


def set_active_camera(params):
    name = params.get("name")
    if not name:
        raise ValueError("set_active_camera requires 'name'")
    obj = bpy.data.objects.get(name)
    if not obj or obj.type != 'CAMERA':
        raise ValueError(f"Camera '{name}' not found")
    bpy.context.scene.camera = obj
    return {"name": obj.name, "active": True}


def create_primitive(params):
    """
    Create a primitive object (cube, sphere, cylinder, cone, torus, plane, monkey).

    Parameters:
        primitive_type: Type of primitive to create
        name: Optional custom name
        location: Optional [x, y, z] location
        rotation: Optional [x, y, z] rotation in degrees
        scale: Optional uniform or [x, y, z] scale
        size: Optional size parameter

    Returns:
        Object info with name, type, location
    """
    import math

    primitive_type = (params.get("primitive_type") or params.get("type", "")).lower()
    name = params.get("name")
    location = params.get("location", [0, 0, 0])
    rotation = params.get("rotation", [0, 0, 0])
    scale_param = params.get("scale", 1.0)
    size = params.get("size", 2.0)

    if not primitive_type:
        raise ValueError("create_primitive requires 'primitive_type' parameter")

    # Map primitive types to operators
    operators = {
        "cube": lambda: bpy.ops.mesh.primitive_cube_add(size=size, location=location),
        "sphere": lambda: bpy.ops.mesh.primitive_uv_sphere_add(radius=size/2, location=location),
        "cylinder": lambda: bpy.ops.mesh.primitive_cylinder_add(radius=size/2, depth=size, location=location),
        "cone": lambda: bpy.ops.mesh.primitive_cone_add(radius1=size/2, depth=size, location=location),
        "torus": lambda: bpy.ops.mesh.primitive_torus_add(major_radius=size/2, minor_radius=size/4, location=location),
        "plane": lambda: bpy.ops.mesh.primitive_plane_add(size=size, location=location),
        "monkey": lambda: bpy.ops.mesh.primitive_monkey_add(size=size, location=location)
    }

    if primitive_type not in operators:
        raise ValueError(f"Unknown primitive_type: {primitive_type}. Supported: {', '.join(operators.keys())}")

    # Create the primitive
    operators[primitive_type]()

    # Get the created object (active object)
    obj = bpy.context.active_object

    # Set custom name if provided
    if name:
        obj.name = name

    # Apply rotation
    obj.rotation_euler = [math.radians(a) for a in rotation]

    # Apply scale
    if isinstance(scale_param, (int, float)):
        obj.scale = (scale_param, scale_param, scale_param)
    else:
        obj.scale = scale_param

    # Update scene
    bpy.context.view_layer.update()

    return {
        "name": obj.name,
        "type": primitive_type,
        "location": list(obj.location),
        "rotation_degrees": rotation,
        "scale": list(obj.scale)
    }


def duplicate_object(params):
    """Duplicate object with optional offset."""
    object_name = params.get("object_name") or params.get("name")
    new_name = params.get("new_name")
    offset = params.get("offset", [0, 0, 0])
    if not object_name:
        raise ValueError("duplicate_object requires 'object_name'")
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")
    new_mesh = obj.data.copy() if obj.data else None
    new_obj = obj.copy()
    if new_mesh:
        new_obj.data = new_mesh
    bpy.context.scene.collection.objects.link(new_obj)
    if new_name:
        new_obj.name = new_name
    new_obj.location = [obj.location[i] + offset[i] for i in range(3)]
    return {"original": object_name, "duplicate": new_obj.name, "location": list(new_obj.location)}

def delete_object(params):
    """Delete object from scene."""
    object_name = params.get("object_name") or params.get("name")
    if not object_name:
        raise ValueError("delete_object requires 'object_name'")
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")
    for collection in obj.users_collection:
        collection.objects.unlink(obj)
    bpy.data.objects.remove(obj, do_unlink=True)
    return {"deleted": object_name, "success": True}

def rename_object(params):
    """Rename object."""
    object_name = params.get("object_name") or params.get("name")
    new_name = params.get("new_name")
    if not object_name or not new_name:
        raise ValueError("rename_object requires 'object_name' and 'new_name'")
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")
    old_name = obj.name
    obj.name = new_name
    return {"old_name": old_name, "new_name": obj.name}


def set_material(params):
    """Create/assign material with color."""
    object_name = params.get("object_name") or params.get("name")
    material_name = params.get("material_name", "Material")
    color = params.get("color", [0.8, 0.8, 0.8, 1.0])
    metallic = params.get("metallic", 0.0)
    roughness = params.get("roughness", 0.5)
    if not object_name:
        raise ValueError("set_material requires 'object_name'")
    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")
    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return {"object_name": object_name, "material_name": mat.name, "color": list(color), "metallic": metallic, "roughness": roughness}

def set_parent(params):
    """Set parent-child relationship."""
    child_name = params.get("child") or params.get("child_name")
    parent_name = params.get("parent") or params.get("parent_name")
    keep_transform = params.get("keep_transform", True)
    if not child_name or not parent_name:
        raise ValueError("set_parent requires 'child' and 'parent'")
    child = bpy.data.objects.get(child_name)
    parent = bpy.data.objects.get(parent_name)
    if not child:
        raise ValueError(f"Child '{child_name}' not found")
    if not parent:
        raise ValueError(f"Parent '{parent_name}' not found")
    child.parent = parent
    if keep_transform:
        child.matrix_parent_inverse = parent.matrix_world.inverted()
    return {"child": child_name, "parent": parent_name, "keep_transform": keep_transform}

def set_smooth_shading(params):
    """Set smooth or flat shading."""
    object_name = params.get("object_name") or params.get("name")
    smooth = params.get("smooth", True)
    if not object_name:
        raise ValueError("set_smooth_shading requires 'object_name'")
    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        raise ValueError(f"Mesh object '{object_name}' not found")
    for poly in obj.data.polygons:
        poly.use_smooth = smooth
    return {"object_name": object_name, "smooth": smooth}

def measure_distance(params):
    """PROTOTYPE: Measure distance between two objects"""
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
            "meters": float(distance),
            "centimeters": float(distance * 100),
        },
        "vector": [
            float(obj2.location.x - obj1.location.x),
            float(obj2.location.y - obj1.location.y),
            float(obj2.location.z - obj1.location.z)
        ]
    }


def execute_python(params):
    """
    META-TOOL: Execute arbitrary Python code in Blender

    This is a development tool for rapid prototyping.
    Allows testing new tool ideas without restarting the bridge.
    """
    import io
    import sys as pysys

    script = params.get("script")
    if not script:
        raise ValueError("execute_python requires 'script' parameter")

    # Prepare execution namespace with common imports
    namespace = {
        'bpy': bpy,
        'math': __import__('math'),
        'mathutils': __import__('mathutils'),
        'Vector': __import__('mathutils').Vector,
        'time': time,
    }

    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    old_stdout = pysys.stdout
    old_stderr = pysys.stderr

    try:
        pysys.stdout = stdout_capture
        pysys.stderr = stderr_capture

        # Execute the script
        exec(script, namespace)

        # Get captured output
        stdout_text = stdout_capture.getvalue()
        stderr_text = stderr_capture.getvalue()

        # Try to extract a return value if 'result' was set
        result_value = namespace.get('result', None)

        return {
            "success": True,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "result": result_value,
            "message": "Script executed successfully"
        }

    except Exception as exc:
        stderr_text = stderr_capture.getvalue()
        return {
            "success": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_text,
            "traceback": traceback.format_exc()
        }

    finally:
        pysys.stdout = old_stdout
        pysys.stderr = old_stderr


def viewport_snapshot(params):
    """
    VISION TOOL: Capture viewport snapshot (UI-only).
    """
    import base64
    import tempfile
    import os

    shading = params.get("shading", "solid")
    projection = params.get("projection", "persp")
    view = params.get("view", "current")  # current, front, back, left, right, top, bottom
    width = params.get("width", 512)
    height = params.get("height", 512)
    return_base64 = params.get("return_base64", False)
    filename = params.get("filename")

    shading_map = {"solid": "SOLID", "wireframe": "WIREFRAME"}
    if shading not in shading_map:
        raise ValueError("shading must be 'solid' or 'wireframe'")

    projection_map = {"persp": "PERSP", "perspective": "PERSP", "ortho": "ORTHO"}
    if projection not in projection_map:
        raise ValueError("projection must be 'persp' or 'ortho'")

    valid_views = ["current", "front", "back", "left", "right", "top", "bottom"]
    if view not in valid_views:
        raise ValueError(f"view must be one of {valid_views}")

    try:
        width = int(width)
        height = int(height)
    except (TypeError, ValueError):
        raise ValueError("width and height must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    if bpy.app.background:
        return {"ok": False, "error": "viewport_snapshot requires Blender UI with a 3D Viewport"}

    window = None
    area = None
    region = None
    for candidate_window in bpy.context.window_manager.windows:
        for candidate_area in candidate_window.screen.areas:
            if candidate_area.type != "VIEW_3D":
                continue
            for candidate_region in candidate_area.regions:
                if candidate_region.type == "WINDOW":
                    window = candidate_window
                    area = candidate_area
                    region = candidate_region
                    break
            if area:
                break
        if area:
            break

    if area is None:
        return {"ok": False, "error": "viewport_snapshot requires Blender UI with a 3D Viewport"}

    space = area.spaces.active
    region_3d = space.region_3d
    scene = bpy.context.scene
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.environ.get("FRIGG_OUTPUT_DIR") or os.path.join(repo_root, "output")
    os.makedirs(output_dir, exist_ok=True)

    original_shading = space.shading.type
    original_view_perspective = region_3d.view_perspective
    original_view_rotation = region_3d.view_rotation.copy()
    original_resolution_x = scene.render.resolution_x
    original_resolution_y = scene.render.resolution_y
    original_filepath = scene.render.filepath

    try:
        space.shading.type = shading_map[shading]
        region_3d.view_perspective = projection_map[projection]

        # Set view orientation if specified
        if view != "current":
            import mathutils
            view_rotations = {
                "front": mathutils.Euler((1.5708, 0, 0), 'XYZ').to_quaternion(),  # 90° on X
                "back": mathutils.Euler((1.5708, 0, 3.14159), 'XYZ').to_quaternion(),
                "right": mathutils.Euler((1.5708, 0, -1.5708), 'XYZ').to_quaternion(),
                "left": mathutils.Euler((1.5708, 0, 1.5708), 'XYZ').to_quaternion(),
                "top": mathutils.Euler((0, 0, 0), 'XYZ').to_quaternion(),
                "bottom": mathutils.Euler((3.14159, 0, 0), 'XYZ').to_quaternion(),
            }
            if view in view_rotations:
                region_3d.view_rotation = view_rotations[view]

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        if filename:
            image_name = filename
            if not image_name.lower().endswith(".png"):
                image_name = f"{image_name}.png"
        else:
            image_name = f"viewport_{width}x{height}_{shading}_{projection}_{timestamp}.png"
        image_path = os.path.join(output_dir, image_name)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name

        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = temp_path

        with bpy.context.temp_override(window=window, area=area, region=region):
            bpy.ops.render.opengl(write_still=True)

        with open(temp_path, "rb") as handle:
            image_data = handle.read()

        os.remove(temp_path)

        with open(image_path, "wb") as handle:
            handle.write(image_data)

        result = {
            "image_path": image_path,
            "width": width,
            "height": height,
            "shading": shading,
            "projection": "ortho" if projection_map[projection] == "ORTHO" else "persp",
            "view": view,
        }
        if return_base64:
            result["image_base64"] = base64.b64encode(image_data).decode("utf-8")
        return result
    finally:
        space.shading.type = original_shading
        region_3d.view_perspective = original_view_perspective
        region_3d.view_rotation = original_view_rotation
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.filepath = original_filepath


def get_bounding_box(params):
    """
    SPATIAL COGNITION TOOL: Get bounding box dimensions and bounds

    Returns exact dimensions, world bounds, and volume of an object.
    Critical for understanding object sizes and spatial relationships.
    """
    import mathutils

    object_name = params.get("object_name") or params.get("name")
    if not object_name:
        raise ValueError("get_bounding_box requires 'object_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    if not hasattr(obj, 'bound_box'):
        raise ValueError(f"Object '{object_name}' has no bounding box")

    # Get local bounding box
    bbox_local = obj.bound_box

    # Transform to world space
    matrix_world = obj.matrix_world
    bbox_world = [matrix_world @ mathutils.Vector(corner) for corner in bbox_local]

    # Calculate world space min/max
    min_world = mathutils.Vector((
        min(corner.x for corner in bbox_world),
        min(corner.y for corner in bbox_world),
        min(corner.z for corner in bbox_world)
    ))
    max_world = mathutils.Vector((
        max(corner.x for corner in bbox_world),
        max(corner.y for corner in bbox_world),
        max(corner.z for corner in bbox_world)
    ))

    # Calculate dimensions and center
    dimensions = max_world - min_world
    center = (min_world + max_world) / 2
    volume = dimensions.x * dimensions.y * dimensions.z

    return {
        "object_name": object_name,
        "dimensions": {
            "width": float(dimensions.x),
            "height": float(dimensions.z),  # Z is height in Blender
            "depth": float(dimensions.y),
            "x": float(dimensions.x),
            "y": float(dimensions.y),
            "z": float(dimensions.z),
        },
        "bounds_world": {
            "min": [float(min_world.x), float(min_world.y), float(min_world.z)],
            "max": [float(max_world.x), float(max_world.y), float(max_world.z)],
            "center": [float(center.x), float(center.y), float(center.z)],
        },
        "corners": [[float(c.x), float(c.y), float(c.z)] for c in bbox_world],
        "volume": float(volume),
    }


def get_spatial_relationships(params):
    """
    SPATIAL COGNITION TOOL: Determine spatial relationships between two objects

    Returns relationships like "above", "below", "left_of", "right_of",
    "in_front_of", "behind" based on relative positions in 3D space.

    Parameters:
        object1: First object name
        object2: Second object name (reference point)
        threshold: Minimum distance to consider a relationship (default 0.1)

    Returns:
        Dictionary with:
        - relationships: List of all applicable relationships
        - primary_relationship: The most dominant relationship
        - relative_position: Vector from object2 to object1
        - distance: Euclidean distance between objects
        - positions: World positions of both objects
    """
    import mathutils

    object1_name = params.get("object1") or params.get("object1_name")
    object2_name = params.get("object2") or params.get("object2_name")
    threshold = params.get("threshold", 0.1)

    if not object1_name:
        raise ValueError("get_spatial_relationships requires 'object1' parameter")
    if not object2_name:
        raise ValueError("get_spatial_relationships requires 'object2' parameter")

    obj1 = bpy.data.objects.get(object1_name)
    obj2 = bpy.data.objects.get(object2_name)

    if not obj1:
        raise ValueError(f"Object '{object1_name}' not found")
    if not obj2:
        raise ValueError(f"Object '{object2_name}' not found")

    # Get world locations
    loc1 = obj1.matrix_world.translation
    loc2 = obj2.matrix_world.translation

    # Calculate relative position vector (from obj2 to obj1)
    relative = loc1 - loc2

    # Determine relationships based on axes
    # X axis: left (-) / right (+)
    # Y axis: back (-) / front (+)
    # Z axis: below (-) / above (+)

    relationships = []

    if abs(relative.z) > threshold:
        if relative.z > 0:
            relationships.append("above")
        else:
            relationships.append("below")

    if abs(relative.x) > threshold:
        if relative.x > 0:
            relationships.append("right_of")
        else:
            relationships.append("left_of")

    if abs(relative.y) > threshold:
        if relative.y > 0:
            relationships.append("in_front_of")
        else:
            relationships.append("behind")

    # Calculate distance
    distance = relative.length

    # Determine primary relationship (largest offset)
    primary = None
    if distance > 0:
        max_offset = max(abs(relative.x), abs(relative.y), abs(relative.z))

        if abs(relative.z) == max_offset:
            primary = "above" if relative.z > 0 else "below"
        elif abs(relative.x) == max_offset:
            primary = "right_of" if relative.x > 0 else "left_of"
        elif abs(relative.y) == max_offset:
            primary = "in_front_of" if relative.y > 0 else "behind"

    return {
        "object1": object1_name,
        "object2": object2_name,
        "relationships": relationships,
        "primary_relationship": primary,
        "relative_position": {
            "x": float(relative.x),
            "y": float(relative.y),
            "z": float(relative.z)
        },
        "distance": float(distance),
        "positions": {
            object1_name: [float(loc1.x), float(loc1.y), float(loc1.z)],
            object2_name: [float(loc2.x), float(loc2.y), float(loc2.z)]
        }
    }


# =============================================================================
# SPACE MARINE MODELING TOOLS (v0.5)
# =============================================================================

def add_modifier(params):
    """Add a modifier to an object (Mirror, Subdivision, Boolean, Array, Solidify)"""
    import math

    object_name = params.get("object_name") or params.get("name")
    modifier_type = params.get("modifier_type") or params.get("type")
    custom_name = params.get("name") or params.get("modifier_name")

    if not object_name:
        raise ValueError("add_modifier requires 'object_name' parameter")
    if not modifier_type:
        raise ValueError("add_modifier requires 'modifier_type' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Create modifier
    mod_name = custom_name or f"{modifier_type.capitalize()}Modifier"
    modifier = obj.modifiers.new(name=mod_name, type=modifier_type)

    # Configure based on type
    if modifier_type == "MIRROR":
        modifier.use_axis[0] = params.get("axis_x", True)
        modifier.use_axis[1] = params.get("axis_y", False)
        modifier.use_axis[2] = params.get("axis_z", False)
        bisect = params.get("use_bisect_axis", [False, False, False])
        if len(bisect) >= 3:
            modifier.use_bisect_axis[0] = bisect[0]
            modifier.use_bisect_axis[1] = bisect[1]
            modifier.use_bisect_axis[2] = bisect[2]

    elif modifier_type == "SUBSURF":
        modifier.levels = params.get("levels", 2)
        modifier.render_levels = params.get("render_levels", 2)

    elif modifier_type == "BOOLEAN":
        operation = params.get("operation", "DIFFERENCE")
        modifier.operation = operation
        target_name = params.get("target_object")
        if target_name:
            target_obj = bpy.data.objects.get(target_name)
            if target_obj:
                modifier.object = target_obj

    elif modifier_type == "ARRAY":
        modifier.count = params.get("count", 2)
        modifier.relative_offset_displace[0] = params.get("offset_x", 2.0)
        modifier.relative_offset_displace[1] = params.get("offset_y", 0.0)
        modifier.relative_offset_displace[2] = params.get("offset_z", 0.0)

    elif modifier_type == "SOLIDIFY":
        modifier.thickness = params.get("thickness", 0.1)
        modifier.offset = params.get("offset", 0.0)

    return {
        "object": object_name,
        "modifier_name": modifier.name,
        "modifier_type": modifier_type,
        "status": "added"
    }


def apply_modifier(params):
    """Apply (bake) a modifier to make it permanent"""
    object_name = params.get("object_name") or params.get("name")
    modifier_name = params.get("modifier_name")

    if not object_name:
        raise ValueError("apply_modifier requires 'object_name' parameter")
    if not modifier_name:
        raise ValueError("apply_modifier requires 'modifier_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    modifier = obj.modifiers.get(modifier_name)
    if not modifier:
        raise ValueError(f"Modifier '{modifier_name}' not found on '{object_name}'")

    # Apply modifier
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier_name)

    return {
        "object": object_name,
        "modifier": modifier_name,
        "status": "applied"
    }


def list_modifiers(params):
    """List all modifiers on an object"""
    object_name = params.get("object_name") or params.get("name")

    if not object_name:
        raise ValueError("list_modifiers requires 'object_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    modifiers = []
    for mod in obj.modifiers:
        mod_info = {
            "name": mod.name,
            "type": mod.type,
            "show_viewport": mod.show_viewport,
            "show_render": mod.show_render
        }

        # Add type-specific info
        if mod.type == "MIRROR":
            mod_info["axes"] = {
                "x": mod.use_axis[0],
                "y": mod.use_axis[1],
                "z": mod.use_axis[2]
            }
        elif mod.type == "SUBSURF":
            mod_info["levels"] = mod.levels
            mod_info["render_levels"] = mod.render_levels
        elif mod.type == "BOOLEAN":
            mod_info["operation"] = mod.operation
            mod_info["target"] = mod.object.name if mod.object else None

        modifiers.append(mod_info)

    return {
        "object": object_name,
        "modifier_count": len(modifiers),
        "modifiers": modifiers
    }


def boolean_operation(params):
    """Perform boolean operation between two objects"""
    base_name = params.get("base_object") or params.get("object_name")
    target_name = params.get("target_object") or params.get("tool_object")
    operation = params.get("operation", "DIFFERENCE")
    apply_immediately = params.get("apply", False)
    hide_target = params.get("hide_target", True)

    if not base_name:
        raise ValueError("boolean_operation requires 'base_object' parameter")
    if not target_name:
        raise ValueError("boolean_operation requires 'target_object' parameter")

    base_obj = bpy.data.objects.get(base_name)
    target_obj = bpy.data.objects.get(target_name)

    if not base_obj:
        raise ValueError(f"Base object '{base_name}' not found")
    if not target_obj:
        raise ValueError(f"Target object '{target_name}' not found")

    # Add boolean modifier
    modifier = base_obj.modifiers.new(name=f"Boolean_{target_name}", type="BOOLEAN")
    modifier.operation = operation
    modifier.object = target_obj

    result = {
        "base_object": base_name,
        "target_object": target_name,
        "operation": operation,
        "modifier_name": modifier.name,
        "applied": False
    }

    # Apply if requested
    if apply_immediately:
        bpy.context.view_layer.objects.active = base_obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        result["applied"] = True

    # Hide target object
    if hide_target:
        target_obj.hide_set(True)
        result["target_hidden"] = True

    return result


def create_material(params):
    """Create a new PBR material with Principled BSDF"""
    mat_name = params.get("name") or params.get("material_name")
    if not mat_name:
        raise ValueError("create_material requires 'name' parameter")

    # Check if material exists
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)

    # Enable nodes
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    # Create Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Set properties
    base_color = params.get("base_color", [0.8, 0.8, 0.8, 1.0])
    if len(base_color) >= 4:
        bsdf.inputs['Base Color'].default_value = base_color

    metallic = params.get("metallic", 0.0)
    bsdf.inputs['Metallic'].default_value = metallic

    roughness = params.get("roughness", 0.5)
    bsdf.inputs['Roughness'].default_value = roughness

    return {
        "material_name": mat_name,
        "base_color": base_color,
        "metallic": metallic,
        "roughness": roughness,
        "status": "created"
    }


def assign_material(params):
    """Assign a material to an object"""
    object_name = params.get("object_name") or params.get("name")
    material_name = params.get("material_name") or params.get("material")
    slot_index = params.get("slot_index", 0)

    if not object_name:
        raise ValueError("assign_material requires 'object_name' parameter")
    if not material_name:
        raise ValueError("assign_material requires 'material_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    mat = bpy.data.materials.get(material_name)
    if not mat:
        raise ValueError(f"Material '{material_name}' not found")

    # Ensure object has material slots
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        if slot_index >= len(obj.data.materials):
            obj.data.materials.append(mat)
        else:
            obj.data.materials[slot_index] = mat

    return {
        "object": object_name,
        "material": material_name,
        "slot": slot_index,
        "status": "assigned"
    }


def create_collection(params):
    """Create a new collection for organizing objects"""
    collection_name = params.get("name") or params.get("collection_name")
    parent_name = params.get("parent_collection")

    if not collection_name:
        raise ValueError("create_collection requires 'name' parameter")

    # Check if collection exists
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
        status = "exists"
    else:
        collection = bpy.data.collections.new(collection_name)
        status = "created"

        # Link to parent or scene
        if parent_name:
            parent = bpy.data.collections.get(parent_name)
            if parent:
                parent.children.link(collection)
            else:
                raise ValueError(f"Parent collection '{parent_name}' not found")
        else:
            bpy.context.scene.collection.children.link(collection)

    return {
        "collection_name": collection_name,
        "parent": parent_name,
        "status": status
    }


def move_to_collection(params):
    """Move an object to a collection"""
    object_name = params.get("object_name") or params.get("name")
    collection_name = params.get("collection_name") or params.get("collection")
    unlink_current = params.get("unlink_from_current", True)

    if not object_name:
        raise ValueError("move_to_collection requires 'object_name' parameter")
    if not collection_name:
        raise ValueError("move_to_collection requires 'collection_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    collection = bpy.data.collections.get(collection_name)
    if not collection:
        raise ValueError(f"Collection '{collection_name}' not found")

    # Unlink from current collections
    old_collections = []
    if unlink_current:
        for col in obj.users_collection:
            col.objects.unlink(obj)
            old_collections.append(col.name)

    # Link to new collection
    collection.objects.link(obj)

    return {
        "object": object_name,
        "new_collection": collection_name,
        "unlinked_from": old_collections if unlink_current else [],
        "status": "moved"
    }


# =============================================================================
# MESH EDITING TOOLS
# =============================================================================

def join_objects(params):
    """Join multiple mesh objects into one."""
    import bmesh

    try:
        object_names = params.get("object_names") or []
        result_name = params.get("result_name")

        if not isinstance(object_names, list) or len(object_names) < 2:
            raise ValueError("Need at least 2 object names to join.")

        objects = []
        for name in object_names:
            if not name:
                raise ValueError("Object name cannot be empty.")
            obj = bpy.data.objects.get(name)
            if not obj:
                raise ValueError(f"Object '{name}' not found.")
            if obj.type != "MESH":
                raise ValueError(f"Object '{name}' is not a mesh.")
            objects.append(obj)

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()

        result_obj = bpy.context.view_layer.objects.active
        if not result_obj or result_obj.type != "MESH":
            raise ValueError("Join operation failed to produce a mesh result.")

        if result_name:
            result_obj.name = result_name

        mesh = result_obj.data
        return {
            "result_object": result_obj.name,
            "vertex_count": len(mesh.vertices),
            "face_count": len(mesh.polygons),
            "merged_objects": object_names,
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


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

        if direction is not None:
            if (
                not isinstance(direction, (list, tuple))
                or len(direction) != 3
                or not all(isinstance(v, (int, float)) for v in direction)
            ):
                raise ValueError("direction must be [x, y, z] if provided.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

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
        else:
            raise ValueError("face_indices must be a list of integers or 'all'.")

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        if not selected_faces:
            raise ValueError("No faces selected for extrusion.")

        # Extrude the selected faces
        bpy.ops.mesh.extrude_region()

        # Then move them
        if direction is None:
            # Shrink/fatten along normals
            bpy.ops.transform.shrink_fatten(value=float(offset))
        else:
            # Translate in specific direction
            translation = tuple(float(direction[i]) * float(offset) for i in range(3))
            bpy.ops.transform.translate(value=translation)

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


def inset_faces(params):
    """Inset faces on a mesh object."""
    import bmesh

    try:
        object_name = params.get("object_name")
        face_indices = params.get("face_indices")
        thickness = params.get("thickness", 0.1)
        depth = params.get("depth", 0.0)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if face_indices is None:
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
        else:
            raise ValueError("face_indices must be a list of integers.")

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        if not selected_faces:
            raise ValueError("No faces selected for inset.")

        bpy.ops.mesh.inset(thickness=float(thickness), depth=float(depth))
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "inset_faces": selected_faces,
            "new_face_count": len(obj.data.polygons),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def merge_vertices(params):
    """Merge vertices by distance (remove doubles)."""
    import bmesh

    try:
        object_name = params.get("object_name")
        distance = params.get("distance", 0.0001)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")
        if distance is None or float(distance) < 0:
            raise ValueError("distance must be a non-negative number.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        vertices_before = len(bm.verts)

        bpy.ops.mesh.remove_doubles(threshold=float(distance))
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        bm = bmesh.from_edit_mesh(obj.data)
        vertices_after = len(bm.verts)

        return {
            "object": obj.name,
            "vertices_before": vertices_before,
            "vertices_after": vertices_after,
            "removed_count": max(0, vertices_before - vertices_after),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def bevel_edges(params):
    """Bevel edges on a mesh object."""
    import bmesh

    try:
        object_name = params.get("object_name")
        edge_indices = params.get("edge_indices")
        width = params.get("width", 0.1)
        segments = params.get("segments", 2)
        profile = params.get("profile", 0.5)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        if edge_indices is None or edge_indices == "all":
            for edge in bm.edges:
                edge.select = True
            selected_edges = [edge.index for edge in bm.edges]
        elif isinstance(edge_indices, list):
            try:
                indices = {int(i) for i in edge_indices}
            except (TypeError, ValueError):
                raise ValueError("edge_indices must be a list of integers.")
            selected_edges = []
            for edge in bm.edges:
                edge.select = edge.index in indices
                if edge.select:
                    selected_edges.append(edge.index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        bpy.ops.mesh.bevel(offset=float(width), segments=int(segments), profile=float(profile))

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "beveled_edges": selected_edges,
            "new_vertex_count": len(obj.data.vertices),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def subdivide_mesh(params):
    """Subdivide mesh faces."""
    import bmesh

    try:
        object_name = params.get("object_name")
        cuts = params.get("cuts", 1)
        smooth = params.get("smooth", 0.0)
        face_indices = params.get("face_indices")

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if face_indices is None:
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

        bpy.ops.mesh.subdivide(number_cuts=int(cuts), smoothness=float(smooth))

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "subdivided_faces": selected_faces,
            "new_vertex_count": len(obj.data.vertices),
            "new_face_count": len(obj.data.polygons),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def recalculate_normals(params):
    """Recalculate face normals (fix inside-out faces)."""
    import bmesh

    try:
        object_name = params.get("object_name")
        inside = params.get("inside", False)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bpy.ops.mesh.normals_make_consistent(inside=bool(inside))

        return {
            "object": obj.name,
            "status": "recalculated",
            "face_count": len(obj.data.polygons),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def shade_smooth(params):
    """Set smooth or flat shading on a mesh object."""
    try:
        object_name = params.get("object_name")
        smooth = params.get("smooth", True)
        auto_smooth = params.get("auto_smooth", False)
        angle = params.get("angle", 30.0)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        if smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()

        if auto_smooth:
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = float(angle) * 3.14159 / 180.0

        return {
            "object": obj.name,
            "shading": "smooth" if smooth else "flat",
            "auto_smooth": auto_smooth,
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def apply_all_modifiers(params):
    """Apply all modifiers on an object."""
    try:
        object_name = params.get("object_name")
        modifier_types = params.get("types")

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        applied = []
        for modifier in list(obj.modifiers):
            if modifier_types is None or modifier.type in modifier_types:
                try:
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                    applied.append(modifier.name)
                except Exception as e:
                    pass

        return {
            "object": obj.name,
            "applied_modifiers": applied,
            "count": len(applied),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def select_faces_by_angle(params):
    """Select faces by their normal direction."""
    import bmesh
    import math

    try:
        object_name = params.get("object_name")
        direction = params.get("direction", [0, 0, 1])
        threshold = params.get("threshold", 10.0)
        extend = params.get("extend", False)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        if not extend:
            bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        import mathutils
        target = mathutils.Vector(direction).normalized()
        threshold_rad = math.radians(float(threshold))

        selected = []
        for face in bm.faces:
            angle = face.normal.angle(target)
            if angle < threshold_rad:
                face.select = True
                selected.append(face.index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "selected_faces": selected,
            "count": len(selected),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_request(request):
    method = request.get("method") if isinstance(request, dict) else None
    params = request.get("params", {}) if isinstance(request, dict) else {}

    try:
        if method == "bridge_ping":
            return {"ok": True, "result": {"pong": True, "time": time.time()}}
        if method == "get_scene_info":
            return {"ok": True, "result": scene_info()}
        if method == "get_object_transform":
            return {"ok": True, "result": get_object_transform(params)}
        if method == "set_object_location":
            return {"ok": True, "result": set_object_location(params)}
        if method == "set_object_rotation":
            return {"ok": True, "result": set_object_rotation(params)}
        if method == "set_object_scale":
            return {"ok": True, "result": set_object_scale(params)}
        if method == "select_object":
            return {"ok": True, "result": select_object(params)}
        if method == "get_transform":
            return {"ok": True, "result": get_transform(params)}
        if method == "set_transform":
            return {"ok": True, "result": set_transform(params)}
        if method == "apply_transform":
            return {"ok": True, "result": apply_transform(params)}
        if method == "create_camera":
            return {"ok": True, "result": create_camera(params)}
        if method == "set_active_camera":
            return {"ok": True, "result": set_active_camera(params)}
        if method == "create_primitive":
            return {"ok": True, "result": create_primitive(params)}
        if method == "duplicate_object":
            return {"ok": True, "result": duplicate_object(params)}
        if method == "delete_object":
            return {"ok": True, "result": delete_object(params)}
        if method == "rename_object":
            return {"ok": True, "result": rename_object(params)}
        if method == "set_material":
            return {"ok": True, "result": set_material(params)}
        if method == "set_parent":
            return {"ok": True, "result": set_parent(params)}
        if method == "set_smooth_shading":
            return {"ok": True, "result": set_smooth_shading(params)}
        if method == "scene_info":
            return {"ok": True, "result": scene_info()}
        if method == "list_objects":
            return {"ok": True, "result": list_objects()}
        if method == "move_object":
            return {"ok": True, "result": move_object(params)}

        # VISION TOOLS - Core vision capabilities
        if method == "viewport_snapshot":
            result = viewport_snapshot(params)
            if isinstance(result, dict) and result.get("ok") is False and "error" in result:
                return result
            return {"ok": True, "result": result}

        # SPATIAL COGNITION TOOLS
        if method == "get_bounding_box":
            return {"ok": True, "result": get_bounding_box(params)}
        if method == "get_spatial_relationships":
            return {"ok": True, "result": get_spatial_relationships(params)}
        if method == "measure_distance":
            return {"ok": True, "result": measure_distance(params)}

        # META-TOOLS - Development utilities
        if method == "execute_python":
            return {"ok": True, "result": execute_python(params)}

        # SPACE MARINE MODELING TOOLS (v0.5)
        if method == "add_modifier":
            return {"ok": True, "result": add_modifier(params)}
        if method == "apply_modifier":
            return {"ok": True, "result": apply_modifier(params)}
        if method == "list_modifiers":
            return {"ok": True, "result": list_modifiers(params)}
        if method == "boolean_operation":
            return {"ok": True, "result": boolean_operation(params)}
        if method == "create_material":
            return {"ok": True, "result": create_material(params)}
        if method == "assign_material":
            return {"ok": True, "result": assign_material(params)}
        if method == "create_collection":
            return {"ok": True, "result": create_collection(params)}
        if method == "move_to_collection":
            return {"ok": True, "result": move_to_collection(params)}

        # MESH EDITING TOOLS
        if method == "join_objects":
            return {"ok": True, "result": join_objects(params)}
        if method == "extrude_faces":
            return {"ok": True, "result": extrude_faces(params)}
        if method == "inset_faces":
            return {"ok": True, "result": inset_faces(params)}
        if method == "merge_vertices":
            return {"ok": True, "result": merge_vertices(params)}
        if method == "bevel_edges":
            return {"ok": True, "result": bevel_edges(params)}
        if method == "subdivide_mesh":
            return {"ok": True, "result": subdivide_mesh(params)}
        if method == "recalculate_normals":
            return {"ok": True, "result": recalculate_normals(params)}
        if method == "shade_smooth":
            return {"ok": True, "result": shade_smooth(params)}
        if method == "apply_all_modifiers":
            return {"ok": True, "result": apply_all_modifiers(params)}
        if method == "select_faces_by_angle":
            return {"ok": True, "result": select_faces_by_angle(params)}

        return {"ok": False, "error": f"Unknown method: {method}"}
    except Exception as exc:
        log(f"Error handling {method}: {exc}")
        log(traceback.format_exc())
        return {"ok": False, "error": str(exc)}


def _queue_request(request):
    job = {"request": request, "event": threading.Event(), "response": None}
    REQUEST_QUEUE.put(job)
    return job


def _process_requests():
    if STOP:
        return None
    while True:
        try:
            job = REQUEST_QUEUE.get_nowait()
        except queue.Empty:
            break
        try:
            job["response"] = handle_request(job["request"])
        except Exception as exc:
            log(f"Error processing request: {exc}")
            log(traceback.format_exc())
            job["response"] = {"ok": False, "error": str(exc)}
        job["event"].set()
    return 0.05


def _accept_loop(server: socket.socket) -> None:
    server.settimeout(0.5)
    while True:
        if STOP:
            break
        try:
            conn, _addr = server.accept()
        except socket.timeout:
            continue
        except OSError:
            break

        with conn:
            file = conn.makefile("r", encoding="utf-8")
            for line in file:
                if STOP:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                    job = _queue_request(request)
                    job["event"].wait()
                    response = job["response"]
                    if response is None:
                        response = {"ok": False, "error": "No response from main thread"}
                except Exception as exc:
                    log(traceback.format_exc())
                    response = {"ok": False, "error": str(exc)}
                payload = json.dumps(response) + "\n"
                conn.sendall(payload.encode("utf-8"))


def _request_shutdown() -> None:
    global STOP
    STOP = True
    while True:
        try:
            job = REQUEST_QUEUE.get_nowait()
        except queue.Empty:
            break
        job["response"] = {"ok": False, "error": "Bridge shutting down"}
        job["event"].set()
    server = SERVER_SOCKET
    if server is not None:
        try:
            server.close()
        except OSError:
            pass


def _register_shutdown_handler() -> None:
    if hasattr(bpy.app.handlers, "quit_pre"):
        bpy.app.handlers.quit_pre.append(lambda _d=None: _request_shutdown())
        return
    try:
        import atexit

        atexit.register(_request_shutdown)
    except Exception:
        pass


def serve(host: str, port: int) -> None:
    global SERVER_SOCKET
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    SERVER_SOCKET = server
    print("READY", flush=True)

    thread = threading.Thread(target=_accept_loop, args=(server,), daemon=True)
    thread.start()
    _register_shutdown_handler()
    bpy.app.timers.register(_process_requests, first_interval=0.05, persistent=True)


if __name__ == "__main__":
    host = os.environ.get("FRIGG_BRIDGE_HOST", "127.0.0.1")
    port_str = os.environ.get("FRIGG_BRIDGE_PORT", "7878")
    try:
        port = int(port_str)
    except ValueError:
        port = 7878

    serve(host, port)
