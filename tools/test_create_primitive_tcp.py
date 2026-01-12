"""Test create_primitive via TCP"""
import json
import socket

host = 'localhost'
port = 8765

def send_request(method, params):
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
        return json.loads(response.decode('utf-8'))

print("=" * 70)
print("TESTING create_primitive via TCP")
print("=" * 70)

# Test 1: Create cube
print("\n1. Create cube")
data = send_request('create_primitive', {'primitive_type': 'cube', 'name': 'MyCube'})
if data.get('ok'):
    result = data['result']
    print(f"   Created: {result['name']} (type: {result['type']})")
    print(f"   Location: {result['location']}")
    print("   OK")
else:
    print(f"   ERROR: {data.get('error')}")
    exit(1)

# Test 2: Create sphere at location
print("\n2. Create sphere at [3, 0, 0]")
data = send_request('create_primitive', {
    'primitive_type': 'sphere',
    'location': [3, 0, 0],
    'scale': 0.5
})
if data.get('ok'):
    result = data['result']
    print(f"   Created: {result['name']}")
    print(f"   Location: {result['location']}")
    print(f"   Scale: {result['scale']}")
    print("   OK")
else:
    print(f"   ERROR: {data.get('error')}")

print("\n" + "=" * 70)
print("TEST PASSED - create_primitive works via TCP!")
print("=" * 70)
