"""Simple TCP test client for Frigg bridge"""
import socket
import json
import sys

host = 'localhost'
port = 8765

if len(sys.argv) < 3:
    print("Usage: python tcp_test.py <method> <code>")
    sys.exit(1)

method = sys.argv[1]
code = sys.argv[2]

request = {
    'method': method,
    'params': {'script': code} if method == 'execute_python' else {}
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

        if 'result' in data:
            print(json.dumps(data['result'], indent=2))
        else:
            print(f"Error: {data.get('error', 'Unknown error')}")

except Exception as e:
    print(f"Exception: {e}")
    sys.exit(1)
