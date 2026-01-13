import json, socket

def call(method, params):
    with socket.create_connection(("127.0.0.1", 8765), timeout=5) as sock:
        sock.sendall((json.dumps({"method": method, "params": params}) + "\n").encode())
        return json.loads(sock.makefile("r").readline())

# Test shade_smooth
call("create_primitive", {"primitive_type": "sphere", "name": "TestSphere", "location": [0, 0, 0]})
r1 = call("shade_smooth", {"object_name": "TestSphere", "smooth": True})
print(f"shade_smooth: {r1}")

# Test apply_all_modifiers
call("create_primitive", {"primitive_type": "cube", "name": "TestCube", "location": [3, 0, 0]})
call("add_modifier", {"object_name": "TestCube", "modifier_type": "SUBSURF", "levels": 2})
r2 = call("apply_all_modifiers", {"object_name": "TestCube"})
print(f"apply_all_modifiers: {r2}")
