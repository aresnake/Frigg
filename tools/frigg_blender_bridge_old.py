import json
import os
import socket
import sys
import threading
import time
import traceback

import bpy

STOP = False
SERVER_SOCKET = None


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
    VISION TOOL: Capture viewport screenshot

    This is the fundamental vision tool for the LLM.
    Allows seeing the scene while working.
    """
    import base64
    import tempfile

    # Parameters with defaults
    shading = params.get("shading", "solid")  # solid | wireframe | material | rendered
    projection = params.get("projection", "perspective")  # perspective | ortho
    view = params.get("view", "current")  # current | camera | front | back | left | right | top | bottom
    width = params.get("width", 512)
    height = params.get("height", 512)
    format_type = params.get("format", "PNG")  # PNG | JPEG

    # Optional parameters
    target = params.get("target", None)  # Object or collection name to focus on
    isolate = params.get("isolate", False)  # Hide everything except target
    fit_to_view = params.get("fit_to_view", False)  # Frame target in view
    show_overlays = params.get("show_overlays", True)

    # Validate parameters
    valid_shadings = ["solid", "wireframe", "material", "rendered"]
    if shading not in valid_shadings:
        raise ValueError(f"shading must be one of {valid_shadings}, got '{shading}'")

    valid_projections = ["perspective", "ortho"]
    if projection not in valid_projections:
        raise ValueError(f"projection must be one of {valid_projections}, got '{projection}'")

    valid_views = ["current", "camera", "front", "back", "left", "right", "top", "bottom"]
    if view not in valid_views:
        raise ValueError(f"view must be one of {valid_views}, got '{view}'")

    # Get the 3D viewport area
    area = None
    for window in bpy.context.window_manager.windows:
        for a in window.screen.areas:
            if a.type == 'VIEW_3D':
                area = a
                break
        if area:
            break

    if not area:
        raise RuntimeError("No 3D viewport found")

    # Get the space_data
    space = area.spaces.active

    # Store original settings to restore later
    original_shading = space.shading.type
    original_overlay = space.overlay.show_overlays

    # Store original view settings
    region_3d = space.region_3d
    original_view_perspective = region_3d.view_perspective
    original_view_rotation = region_3d.view_rotation.copy()
    original_view_location = region_3d.view_location.copy()
    original_view_distance = region_3d.view_distance

    # Store visibility states if isolating
    original_visibility = {}
    if isolate and target:
        for obj in bpy.data.objects:
            original_visibility[obj.name] = obj.hide_get()

    try:
        # Apply shading mode
        shading_map = {
            "solid": "SOLID",
            "wireframe": "WIREFRAME",
            "material": "MATERIAL",
            "rendered": "RENDERED"
        }
        space.shading.type = shading_map[shading]

        # Apply overlay setting
        space.overlay.show_overlays = show_overlays

        # Apply projection
        if projection == "ortho":
            region_3d.view_perspective = 'ORTHO'
        else:
            region_3d.view_perspective = 'PERSP'

        # Apply view orientation
        if view == "camera":
            region_3d.view_perspective = 'CAMERA'
        elif view != "current":
            # Set to orthographic view for standard views
            region_3d.view_perspective = 'ORTHO'

            # View orientations (quaternions)
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

        # Handle target isolation
        if target:
            target_obj = bpy.data.objects.get(target)
            if not target_obj:
                raise ValueError(f"Target object '{target}' not found")

            if isolate:
                # Hide all objects except target
                for obj in bpy.data.objects:
                    obj.hide_set(obj.name != target)

            if fit_to_view:
                # Select and frame the target
                bpy.ops.object.select_all(action='DESELECT')
                target_obj.select_set(True)
                bpy.context.view_layer.objects.active = target_obj

                # Frame selected
                for window in bpy.context.window_manager.windows:
                    for a in window.screen.areas:
                        if a.type == 'VIEW_3D':
                            for region in a.regions:
                                if region.type == 'WINDOW':
                                    with bpy.context.temp_override(window=window, area=a, region=region):
                                        bpy.ops.view3d.view_selected()
                            break

        # Create temporary file for render
        with tempfile.NamedTemporaryFile(suffix=f".{format_type.lower()}", delete=False) as tmp:
            temp_path = tmp.name

        # Set render resolution
        scene = bpy.context.scene
        original_resolution_x = scene.render.resolution_x
        original_resolution_y = scene.render.resolution_y
        original_filepath = scene.render.filepath

        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = temp_path

        # Render viewport using temp_override to provide correct context
        for window in bpy.context.window_manager.windows:
            for a in window.screen.areas:
                if a.type == 'VIEW_3D':
                    for region in a.regions:
                        if region.type == 'WINDOW':
                            with bpy.context.temp_override(window=window, area=a, region=region):
                                bpy.ops.render.opengl(write_still=True)
                            break
                    break
            break

        # Read the image and encode to base64
        with open(temp_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        # Clean up temp file
        os.remove(temp_path)

        # Restore resolution and filepath
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.filepath = original_filepath

        # Prepare view info
        view_info = {
            "shading": shading,
            "projection": projection,
            "view": view,
            "camera_location": list(region_3d.view_location),
            "camera_rotation": list(region_3d.view_rotation),
            "viewport_distance": float(region_3d.view_distance)
        }

        return {
            "success": True,
            "image": base64_image,
            "format": format_type,
            "width": width,
            "height": height,
            "view_info": view_info
        }

    finally:
        # Restore original settings
        space.shading.type = original_shading
        space.overlay.show_overlays = original_overlay
        region_3d.view_perspective = original_view_perspective
        region_3d.view_rotation = original_view_rotation
        region_3d.view_location = original_view_location
        region_3d.view_distance = original_view_distance

        # Restore visibility
        if isolate and target:
            for obj_name, was_hidden in original_visibility.items():
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.hide_set(was_hidden)


def handle_request(request):
    method = request.get("method")
    params = request.get("params", {})

    try:
        if method == "bridge_ping":
            return {"ok": True, "result": {"pong": True, "time": time.time()}}
        if method == "get_object_transform":
            return {"result": get_object_transform(params)}
        if method == "set_object_location":
            return {"result": set_object_location(params)}
        if method == "scene_info":
            return {"result": scene_info()}
        if method == "list_objects":
            return {"result": list_objects()}
        if method == "move_object":
            return {"result": move_object(params)}

        # VISION TOOLS - Core vision capabilities
        if method == "viewport_snapshot":
            return {"result": viewport_snapshot(params)}

        # PROTOTYPE TOOLS - Testing new features
        if method == "measure_distance":
            return {"result": measure_distance(params)}

        # META-TOOLS - Development utilities
        if method == "execute_python":
            return {"result": execute_python(params)}

        return {"error": f"Unknown method: {method}"}
    except Exception as exc:
        log(f"Error handling {method}: {exc}")
        log(traceback.format_exc())
        return {"error": str(exc)}


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
                    response = handle_request(request)
                except Exception as exc:
                    log(traceback.format_exc())
                    response = {"error": str(exc)}
                payload = json.dumps(response) + "\n"
                conn.sendall(payload.encode("utf-8"))


def _keepalive():
    if STOP:
        return None
    return 0.5


def _request_shutdown() -> None:
    global STOP
    STOP = True
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
    bpy.app.timers.register(_keepalive, first_interval=0.5, persistent=True)


if __name__ == "__main__":
    host = os.environ.get("FRIGG_BRIDGE_HOST", "127.0.0.1")
    port_str = os.environ.get("FRIGG_BRIDGE_PORT", "7878")
    try:
        port = int(port_str)
    except ValueError:
        port = 7878

    serve(host, port)
