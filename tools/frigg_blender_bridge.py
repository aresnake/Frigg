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
    VISION TOOL: Capture viewport snapshot using camera render

    Uses standard Blender rendering (WORKBENCH engine) instead of viewport opengl
    because the bridge runs without UI context.
    """
    import base64
    import tempfile
    import bpy
    import os
    import mathutils

    # Parameters with defaults
    shading = params.get("shading", "solid")  # solid | wireframe | material | rendered
    projection = params.get("projection", "perspective")  # perspective | ortho
    view = params.get("view", "current")  # current | camera | front | back | left | right | top | bottom
    width = params.get("width", 512)
    height = params.get("height", 512)
    format_type = params.get("format", "PNG")  # PNG | JPEG

    # Optional parameters
    target = params.get("target", None)
    isolate = params.get("isolate", False)
    fit_to_view = params.get("fit_to_view", False)

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

    scene = bpy.context.scene

    # Store original settings
    original_resolution_x = scene.render.resolution_x
    original_resolution_y = scene.render.resolution_y
    original_resolution_percentage = scene.render.resolution_percentage
    original_filepath = scene.render.filepath
    original_file_format = scene.render.image_settings.file_format
    original_engine = scene.render.engine

    # Store original camera (if exists)
    original_camera = scene.camera
    temp_camera_created = False

    # Store visibility if isolating
    original_visibility = {}
    if isolate and target:
        for obj in bpy.data.objects:
            original_visibility[obj.name] = obj.hide_render

    try:
        # Create/setup camera for snapshot
        if view == "camera" and original_camera:
            # Use existing camera
            camera = original_camera
        else:
            # Create temporary camera manually (no bpy.ops - no UI context needed!)
            camera_data = bpy.data.cameras.new(name="_frigg_temp_camera_data")
            camera = bpy.data.objects.new("_frigg_temp_camera", camera_data)
            scene.collection.objects.link(camera)

            # Update depsgraph before assigning as scene camera to avoid crash
            import bpy
            bpy.context.view_layer.update()

            scene.camera = camera
            temp_camera_created = True

            # Position camera based on view
            if view == "current":
                # Try to get current viewport view
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            space = area.spaces.active
                            region_3d = space.region_3d

                            # Copy viewport camera position
                            camera.location = region_3d.view_location.copy()
                            camera.rotation_euler = region_3d.view_rotation.to_euler()

                            # Adjust distance
                            view_dir = region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
                            camera.location -= view_dir * region_3d.view_distance
                            break
                    break
            else:
                # Standard orthographic views
                view_configs = {
                    "front": ((0, -10, 0), (90, 0, 0)),
                    "back": ((0, 10, 0), (90, 0, 180)),
                    "right": ((10, 0, 0), (90, 0, 90)),
                    "left": ((-10, 0, 0), (90, 0, -90)),
                    "top": ((0, 0, 10), (0, 0, 0)),
                    "bottom": ((0, 0, -10), (180, 0, 0))
                }

                if view in view_configs:
                    loc, rot = view_configs[view]
                    camera.location = loc
                    camera.rotation_euler = [r * 3.14159 / 180 for r in rot]

        # Set camera projection
        if projection == "ortho":
            camera.data.type = 'ORTHO'
            camera.data.ortho_scale = 10.0  # Default ortho scale
        else:
            camera.data.type = 'PERSP'

        # Handle target isolation and framing
        if target:
            target_obj = bpy.data.objects.get(target)
            if not target_obj:
                raise ValueError(f"Target object '{target}' not found")

            if isolate:
                # Hide all objects except target in render
                for obj in bpy.data.objects:
                    obj.hide_render = (obj.name != target)

            if fit_to_view:
                # Point camera at target
                direction = target_obj.location - camera.location
                rot_quat = direction.to_track_quat('-Z', 'Y')
                camera.rotation_euler = rot_quat.to_euler()

        # Setup render settings
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = format_type

        # Set render engine based on shading
        if shading == "rendered":
            # Keep original engine (EEVEE/CYCLES)
            pass
        elif shading == "material":
            scene.render.engine = 'BLENDER_EEVEE'
        else:
            # Use WORKBENCH for solid/wireframe (fastest)
            scene.render.engine = 'BLENDER_WORKBENCH'

            # Configure workbench shading
            if shading == "wireframe":
                scene.display.shading.type = 'WIREFRAME'
            else:  # solid
                scene.display.shading.type = 'SOLID'

        # Create temp file path
        with tempfile.NamedTemporaryFile(suffix=f".{format_type.lower()}", delete=False) as tmp:
            temp_path = tmp.name

        scene.render.filepath = temp_path

        # Render!
        bpy.ops.render.render(write_still=True)

        # Read image and encode to base64
        if os.path.exists(temp_path):
            with open(temp_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

            # Clean up temp file
            os.remove(temp_path)
        else:
            raise RuntimeError(f"Render file not created at {temp_path}")

        # Prepare result
        view_info = {
            "shading": shading,
            "projection": projection,
            "view": view,
            "camera_location": list(camera.location),
            "camera_rotation": list(camera.rotation_euler),
            "render_engine": scene.render.engine
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
        # Restore settings
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.resolution_percentage = original_resolution_percentage
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_file_format
        scene.render.engine = original_engine
        scene.camera = original_camera

        # Delete temporary camera
        if temp_camera_created and camera:
            bpy.data.objects.remove(camera, do_unlink=True)

        # Restore visibility
        if isolate and target:
            for obj_name, was_hidden in original_visibility.items():
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.hide_render = was_hidden


def handle_request(request):
    method = request.get("method") if isinstance(request, dict) else None
    params = request.get("params", {}) if isinstance(request, dict) else {}

    try:
        if method == "bridge_ping":
            return {"ok": True, "result": {"pong": True, "time": time.time()}}
        if method == "get_object_transform":
            return {"ok": True, "result": get_object_transform(params)}
        if method == "set_object_location":
            return {"ok": True, "result": set_object_location(params)}
        if method == "scene_info":
            return {"ok": True, "result": scene_info()}
        if method == "list_objects":
            return {"ok": True, "result": list_objects()}
        if method == "move_object":
            return {"ok": True, "result": move_object(params)}

        # VISION TOOLS - Core vision capabilities
        if method == "viewport_snapshot":
            return {"ok": True, "result": viewport_snapshot(params)}

        # PROTOTYPE TOOLS - Testing new features
        if method == "measure_distance":
            return {"ok": True, "result": measure_distance(params)}

        # META-TOOLS - Development utilities
        if method == "execute_python":
            return {"ok": True, "result": execute_python(params)}

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
