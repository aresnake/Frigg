from __future__ import annotations

import json
import os
import subprocess
import sys
import time


CORE_TOOLS = [
    "frigg.ping",
    "frigg.blender.bridge_ping",
    "frigg.blender.get_scene_info",
    "frigg.blender.list_objects",
    "frigg.blender.create_primitive",
    "frigg.blender.delete_object",
    "frigg.blender.select_object",
    "frigg.blender.get_transform",
    "frigg.blender.set_transform",
    "frigg.blender.apply_transform",
    "frigg.blender.create_camera",
    "frigg.blender.set_active_camera",
]


def _read_json_line(proc: subprocess.Popen, timeout_s: float = 5.0) -> dict:
    start = time.time()
    buf = ""
    while time.time() - start < timeout_s:
        line = proc.stdout.readline()
        if not line:
            # give the process a moment, then continue
            time.sleep(0.02)
            continue
        buf = line.strip()
        if not buf:
            continue
        return json.loads(buf)
    raise TimeoutError("Timeout waiting for JSON-RPC response")


def send(proc: subprocess.Popen, msg: dict) -> dict:
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()
    return _read_json_line(proc, timeout_s=10.0)


def _assert_tool_list_exact(tools: list[dict]) -> None:
    names = sorted([t.get("name") for t in tools])
    expected = sorted(CORE_TOOLS)
    assert names == expected, f"tools/list mismatch.\nExpected: {expected}\nGot: {names}"


def _assert_ok(response: dict, label: str) -> None:
    result = response.get("result", {})
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise AssertionError(f"{label} failed: {response}")


def _bridge_is_up(proc: subprocess.Popen) -> bool:
    resp = send(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {"name": "frigg.blender.bridge_ping", "arguments": {}},
        },
    )
    r = resp.get("result", {})
    return isinstance(r, dict) and r.get("ok") is True


def test_core_tools_list_only():
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
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        tools_resp = send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = tools_resp.get("result", {}).get("tools", [])
        _assert_tool_list_exact(tools)

        ping_resp = send(
            proc,
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "frigg.ping", "arguments": {}}},
        )
        _assert_ok(ping_resp, "ping")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()


def test_core_golden_path_with_blender_if_available():
    """
    Integration-ish: only runs if the Blender bridge is up.
    This keeps core v0.1 contract test green on machines where Blender isn't running.
    """
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
        send(proc, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})

        if not _bridge_is_up(proc):
            # Skip without failing the suite
            import pytest
            pytest.skip("Blender bridge not running on 127.0.0.1:8765 (run tools/frigg-bridge.ps1)")

        # Golden path
        create_resp = send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "frigg.blender.create_primitive", "arguments": {"type": "CUBE", "name": "CoreCube"}},
            },
        )
        _assert_ok(create_resp, "create_primitive")

        list_resp = send(
            proc,
            {"jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": {"name": "frigg.blender.list_objects", "arguments": {}}},
        )
        _assert_ok(list_resp, "list_objects")

        delete_resp = send(
            proc,
            {"jsonrpc": "2.0", "id": 12, "method": "tools/call", "params": {"name": "frigg.blender.delete_object", "arguments": {"name": "CoreCube"}}},
        )
        _assert_ok(delete_resp, "delete_object")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except Exception:
            proc.kill()
