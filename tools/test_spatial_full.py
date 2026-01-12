"""
Complete test: Create objects, then test spatial relationships
"""
import json
import socket

host = 'localhost'
port = 8765

def send_request(method, params):
    """Send TCP request and return result"""
    request = {'method': method, 'params': params}

    with socket.create_connection((host, port), timeout=30) as sock:
        sock.sendall((json.dumps(request) + '\n').encode('utf-8'))

        response = b''
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            response += chunk
            if b'\n' in chunk:
                break

        data = json.loads(response.decode('utf-8'))
        return data

print("=" * 70)
print("TESTING get_spatial_relationships - Complete workflow")
print("=" * 70)

# Step 1: Create test objects using execute_python
print("\n1. Creating test objects...")
create_script = """
import bpy
import bmesh

# Create TestSphere above Cube
if "TestSphere" not in bpy.data.objects:
    mesh = bpy.data.meshes.new("TestSphereMesh")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.5)
    bm.to_mesh(mesh)
    bm.free()

    sphere = bpy.data.objects.new("TestSphere", mesh)
    bpy.context.scene.collection.objects.link(sphere)
    sphere.location = (2.0, 0.0, 3.0)
    bpy.context.view_layer.update()

result = "created"
"""

data = send_request('execute_python', {'script': create_script})
if data.get('ok'):
    print("   OK - Test objects created")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

# Step 2: Test spatial relationships
print("\n2. Testing spatial relationships...")

data = send_request('get_spatial_relationships', {
    'object1': 'TestSphere',
    'object2': 'Cube'
})

if data.get('ok'):
    result = data['result']
    print(f"\n   Object 1: {result['object1']}")
    print(f"   Object 2: {result['object2']}")
    print(f"   Relationships: {result['relationships']}")
    print(f"   Primary: {result['primary_relationship']}")
    print(f"   Relative position: {result['relative_position']}")
    print(f"   Distance: {result['distance']:.2f}")
    print(f"\n   Positions:")
    for obj, pos in result['positions'].items():
        print(f"     {obj}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

    # Verify expected relationships
    if 'above' in result['relationships'] and 'right_of' in result['relationships']:
        print("\n" + "=" * 70)
        print("TEST PASSED - get_spatial_relationships works correctly!")
        print("=" * 70)
    else:
        print(f"\n   WARNING: Expected 'above' and 'right_of', got {result['relationships']}")
else:
    print(f"   ERROR: {data.get('error')}")
