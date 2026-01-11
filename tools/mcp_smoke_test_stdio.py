import json
import os
import subprocess
import sys
import time


def send(proc, message):
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline().strip()
    if not line:
        raise RuntimeError("No response from server")
    return json.loads(line)


def main():
    env = os.environ.copy()
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env["PYTHONPATH"] = os.path.join(repo_root, "src")

    proc = subprocess.Popen(
        [sys.executable, "-m", "frigg_mcp.server.stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=repo_root,
    )

    try:
        init_resp = send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        print("initialize:", init_resp)

        tools_resp = send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        print("tools/list:", tools_resp)

        time.sleep(0.2)

        scene_resp = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "frigg.blender.scene_info", "arguments": {}},
            },
        )
        print("scene_info:", scene_resp)

        list_resp = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {"name": "frigg.blender.list_objects", "arguments": {}},
            },
        )
        print("list_objects:", list_resp)
    finally:
        proc.terminate()
        proc.wait(timeout=2)


if __name__ == "__main__":
    main()