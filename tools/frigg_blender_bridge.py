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

        # PROTOTYPE TOOLS - Testing new features
        if method == "measure_distance":
            return {"result": measure_distance(params)}

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
