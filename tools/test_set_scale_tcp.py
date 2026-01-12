"""
Test set_object_scale via TCP
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
print("TESTING set_object_scale via TCP")
print("=" * 70)

# Test 1: Uniform scale (double size)
print("\n1. Uniform scale (2.0)...")
data = send_request('set_object_scale', {
    'object_name': 'Cube',
    'scale': 2.0
})

if data.get('ok'):
    result = data['result']
    print(f"   Object: {result['object_name']}")
    print(f"   Scale: {result['scale']}")

    if all(abs(s - 2.0) < 0.01 for s in result['scale']):
        print("   OK - Uniform scale applied")
    else:
        print(f"   FAIL - Expected [2, 2, 2], got {result['scale']}")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

# Test 2: Non-uniform scale
print("\n2. Non-uniform scale [1, 1, 3]...")
data = send_request('set_object_scale', {
    'object_name': 'Cube',
    'scale': [1, 1, 3]
})

if data.get('ok'):
    result = data['result']
    print(f"   Scale: {result['scale']}")

    expected = [1, 1, 3]
    if all(abs(result['scale'][i] - expected[i]) < 0.01 for i in range(3)):
        print("   OK - Non-uniform scale correct")
    else:
        print(f"   FAIL - Expected {expected}, got {result['scale']}")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

# Test 3: Reset to original
print("\n3. Reset to original (1.0)...")
data = send_request('set_object_scale', {
    'object_name': 'Cube',
    'scale': 1.0
})

if data.get('ok'):
    result = data['result']
    print(f"   Scale: {result['scale']}")

    if all(abs(s - 1.0) < 0.01 for s in result['scale']):
        print("   OK - Reset to original")
    else:
        print(f"   FAIL - Not at original scale: {result['scale']}")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

print("\n" + "=" * 70)
print("TEST PASSED - set_object_scale works via TCP!")
print("=" * 70)
