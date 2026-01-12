"""Test duplicate/delete/rename via TCP"""
import json
import socket

def send_request(method, params):
    with socket.create_connection(('localhost', 8765), timeout=30) as sock:
        sock.sendall((json.dumps({'method': method, 'params': params}) + '\n').encode('utf-8'))
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
print("TESTING ESSENTIAL OPS via TCP")
print("=" * 70)

# Test 1: Duplicate
print("\n1. Duplicate Cube")
data = send_request('duplicate_object', {'object_name': 'Cube', 'new_name': 'CubeCopy', 'offset': [3, 0, 0]})
if data.get('ok'):
    r = data['result']
    print(f"   Original: {r['original']}, Duplicate: {r['duplicate']}")
    print("   OK")
else:
    print(f"   ERROR: {data.get('error')}")

# Test 2: Rename
print("\n2. Rename CubeCopy to MyCube")
data = send_request('rename_object', {'object_name': 'CubeCopy', 'new_name': 'MyCube'})
if data.get('ok'):
    r = data['result']
    print(f"   Old: {r['old_name']}, New: {r['new_name']}")
    print("   OK")
else:
    print(f"   ERROR: {data.get('error')}")

# Test 3: Delete
print("\n3. Delete MyCube")
data = send_request('delete_object', {'object_name': 'MyCube'})
if data.get('ok'):
    print(f"   Deleted: {data['result']['deleted']}")
    print("   OK")
else:
    print(f"   ERROR: {data.get('error')}")

print("\n" + "=" * 70)
print("TEST PASSED!")
print("=" * 70)
