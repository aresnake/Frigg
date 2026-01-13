import json, socket, time

def call(method, params):
    with socket.create_connection(("127.0.0.1", 8765), timeout=5) as sock:
        sock.sendall((json.dumps({"method": method, "params": params}) + "\n").encode())
        return json.loads(sock.makefile("r").readline())

call("create_primitive", {"primitive_type": "cube", "name": "TestSelect", "location": [5, 0, 0]})
time.sleep(0.5)
r = call("select_faces_by_angle", {"object_name": "TestSelect", "direction": [0, 0, 1], "threshold": 10})
print(f"select result: {r}")
