"""
Test get_spatial_relationships via TCP bridge
"""
import json
import socket

host = 'localhost'
port = 8765

# Test with TestSphere and Cube (created by inline test)
request = {
    'method': 'get_spatial_relationships',
    'params': {
        'object1': 'TestSphere',
        'object2': 'Cube'
    }
}

print("=" * 70)
print("TESTING get_spatial_relationships via TCP")
print("=" * 70)

try:
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

        if data.get('ok'):
            result = data['result']
            print(f"\nObject 1: {result['object1']}")
            print(f"Object 2: {result['object2']}")
            print(f"Relationships: {result['relationships']}")
            print(f"Primary: {result['primary_relationship']}")
            print(f"Relative position: {result['relative_position']}")
            print(f"Distance: {result['distance']:.2f}")
            print(f"\nPositions:")
            for obj, pos in result['positions'].items():
                print(f"  {obj}: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

            print("\n" + "=" * 70)
            print("TEST PASSED - get_spatial_relationships works via TCP!")
            print("=" * 70)
        else:
            print(f"ERROR: {data.get('error', 'Unknown error')}")

except Exception as e:
    print(f"EXCEPTION: {e}")
