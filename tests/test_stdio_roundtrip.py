import json
import os
import subprocess
import sys


def send(proc, message):
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline().strip()
    if not line:
        raise RuntimeError("No response from server")
    return json.loads(line)


def test_initialize_and_tools_list():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
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
        assert init_resp.get("result", {}).get("serverInfo", {}).get("name") == "frigg-mcp"

        tools_resp = send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = tools_resp.get("result", {}).get("tools", [])
        names = {tool.get("name") for tool in tools}
        assert "frigg.ping" in names
    finally:
        proc.terminate()
        proc.wait(timeout=2)