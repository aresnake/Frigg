import json
import os
import socket
import sys
import traceback

import bpy


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


def handle_request(request):
    method = request.get("method")
    params = request.get("params", {})

    if method == "scene_info":
        return {"result": scene_info()}
    if method == "list_objects":
        return {"result": list_objects()}
    if method == "move_object":
        return {"result": move_object(params)}

    return {"error": f"Unknown method: {method}"}


def serve(host: str, port: int) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)
    print("READY", flush=True)

    while True:
        conn, _addr = server.accept()
        with conn:
            file = conn.makefile("r", encoding="utf-8")
            for line in file:
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


if __name__ == "__main__":
    host = os.environ.get("FRIGG_BRIDGE_HOST", "127.0.0.1")
    port_str = os.environ.get("FRIGG_BRIDGE_PORT", "7878")
    try:
        port = int(port_str)
    except ValueError:
        port = 7878

    serve(host, port)