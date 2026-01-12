"""
Test all viewport_snapshot variations via bridge TCP
"""
import json
import socket

host = 'localhost'
port = 8765

tests = [
    {
        "name": "Solid Perspective Front",
        "params": {"shading": "solid", "projection": "perspective", "view": "front", "width": 256, "height": 256}
    },
    {
        "name": "Wireframe Ortho Top",
        "params": {"shading": "wireframe", "projection": "ortho", "view": "top", "width": 256, "height": 256}
    },
    {
        "name": "Solid Ortho Right",
        "params": {"shading": "solid", "projection": "ortho", "view": "right", "width": 256, "height": 256}
    },
    {
        "name": "Material Perspective Current",
        "params": {"shading": "material", "projection": "perspective", "view": "current", "width": 256, "height": 256}
    },
]

print("=" * 70)
print("TESTING ALL viewport_snapshot VARIATIONS")
print("=" * 70)

passed = 0
failed = 0

for test in tests:
    print(f"\nTest: {test['name']}")

    request = {
        'method': 'viewport_snapshot',
        'params': test['params']
    }

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

            if 'result' in data and data['result'].get('success'):
                res = data['result']
                print(f"  PASS - {res['width']}x{res['height']} {res['format']}, {len(res['image'])} chars")
                passed += 1
            else:
                print(f"  FAIL - {data.get('error', 'Unknown error')}")
                failed += 1

    except Exception as e:
        print(f"  FAIL - Exception: {e}")
        failed += 1

print("\n" + "=" * 70)
print(f"RESULTS: {passed} passed, {failed} failed")
print("=" * 70)
