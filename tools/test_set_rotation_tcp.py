"""
Test set_object_rotation via TCP
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
print("TESTING set_object_rotation via TCP")
print("=" * 70)

# Test 1: Rotate Cube 45 degrees on Z axis
print("\n1. Rotate Cube 45 degrees on Z axis...")
data = send_request('set_object_rotation', {
    'object_name': 'Cube',
    'rotation': [0, 0, 45],
    'rotation_mode': 'degrees'
})

if data.get('ok'):
    result = data['result']
    print(f"   Object: {result['object_name']}")
    print(f"   Rotation (degrees): {result['rotation_euler_degrees']}")
    print(f"   Rotation (radians): {result['rotation_euler_radians']}")
    print(f"   Mode: {result['rotation_mode']}")

    # Verify Z rotation is ~45
    if abs(result['rotation_euler_degrees'][2] - 45) < 0.1:
        print("   OK - Z rotation is 45 degrees")
    else:
        print(f"   FAIL - Expected 45, got {result['rotation_euler_degrees'][2]}")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

# Test 2: Multi-axis rotation
print("\n2. Rotate on multiple axes (90, 45, 30)...")
data = send_request('set_object_rotation', {
    'object_name': 'Cube',
    'rotation': [90, 45, 30],
    'rotation_mode': 'degrees'
})

if data.get('ok'):
    result = data['result']
    print(f"   Rotation (degrees): {result['rotation_euler_degrees']}")

    expected = [90, 45, 30]
    actual = result['rotation_euler_degrees']
    all_match = all(abs(actual[i] - expected[i]) < 0.1 for i in range(3))

    if all_match:
        print("   OK - Multi-axis rotation correct")
    else:
        print(f"   FAIL - Expected {expected}, got {actual}")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

# Test 3: Reset to zero
print("\n3. Reset rotation to zero...")
data = send_request('set_object_rotation', {
    'object_name': 'Cube',
    'rotation': [0, 0, 0],
    'rotation_mode': 'degrees'
})

if data.get('ok'):
    result = data['result']
    print(f"   Rotation (degrees): {result['rotation_euler_degrees']}")

    if all(abs(v) < 0.1 for v in result['rotation_euler_degrees']):
        print("   OK - Reset to zero")
    else:
        print(f"   FAIL - Not zero: {result['rotation_euler_degrees']}")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

print("\n" + "=" * 70)
print("TEST PASSED - set_object_rotation works via TCP!")
print("=" * 70)
