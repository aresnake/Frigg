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
    VISION TOOL: Capture viewport snapshot (UI-only).
    """
    import base64
    import tempfile
    import os

    shading = params.get("shading", "solid")
    projection = params.get("projection", "persp")
    width = params.get("width", 512)
    height = params.get("height", 512)

    shading_map = {"solid": "SOLID", "wireframe": "WIREFRAME"}
    if shading not in shading_map:
        raise ValueError("shading must be 'solid' or 'wireframe'")

    projection_map = {"persp": "PERSP", "perspective": "PERSP", "ortho": "ORTHO"}
    if projection not in projection_map:
        raise ValueError("projection must be 'persp' or 'ortho'")

    try:
        width = int(width)
        height = int(height)
    except (TypeError, ValueError):
        raise ValueError("width and height must be integers")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

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
        raise RuntimeError("Viewport snapshot requires a visible 3D View UI")

    space = area.spaces.active
    region_3d = space.region_3d
    scene = bpy.context.scene

    original_shading = space.shading.type
    original_view_perspective = region_3d.view_perspective
    original_resolution_x = scene.render.resolution_x
    original_resolution_y = scene.render.resolution_y
    original_filepath = scene.render.filepath

    try:
        space.shading.type = shading_map[shading]
        region_3d.view_perspective = projection_map[projection]

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

        return {
            "image": base64.b64encode(image_data).decode("utf-8"),
            "format": "png",
            "width": width,
            "height": height,
            "shading": shading,
            "projection": "ortho" if projection_map[projection] == "ORTHO" else "persp",
        }
    finally:
        space.shading.type = original_shading
        region_3d.view_perspective = original_view_perspective
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.filepath = original_filepath


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
