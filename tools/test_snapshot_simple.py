"""
Simple test script to call viewport_snapshot via bridge
"""
import json
import socket

host = 'localhost'
port = 8765

# Test 1: Basic snapshot
print('TEST 1: Basic viewport snapshot (solid, perspective, current)')

request = {
    'method': 'viewport_snapshot',
    'params': {
        'shading': 'solid',
        'projection': 'perspective',
        'view': 'current',
        'width': 256,
        'height': 256
    }
}

try:
    with socket.create_connection((host, port), timeout=30) as sock:
        sock.sendall((json.dumps(request) + '\n').encode('utf-8'))

        # Read response
        response = b''
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            response += chunk
            if b'\n' in chunk:
                break

        data = json.loads(response.decode('utf-8'))

        if 'result' in data:
            res = data['result']
            if res.get('success'):
                print(f'  SUCCESS!')
                print(f'    Resolution: {res["width"]}x{res["height"]}')
                print(f'    Format: {res["format"]}')
                print(f'    Shading: {res["view_info"]["shading"]}')
                print(f'    View: {res["view_info"]["view"]}')
                print(f'    Image length: {len(res["image"])} chars (base64)')
                print(f'    First 50 chars: {res["image"][:50]}...')
            else:
                print(f'  FAILED: {res}')
        elif 'error' in data:
            print(f'  ERROR: {data["error"]}')
        else:
            print(f'  Unexpected response: {data}')

except Exception as e:
    print(f'  EXCEPTION: {e}')
    import traceback
    traceback.print_exc()

print('\nTest complete.')
