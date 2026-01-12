from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Dict


def rpc(req: Dict[str, Any]) -> Dict[str, Any]:
    p = subprocess.run(
        ["pwsh", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "tools/frigg-stdio.ps1"],
        input=(json.dumps(req) + "\n").encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    out = p.stdout.decode("utf-8", errors="replace").strip().splitlines()
    if not out:
        return {"ok": False, "error": {"code": "no_output", "message": p.stderr.decode("utf-8", errors="replace")}}
    try:
        return json.loads(out[-1])
    except Exception as e:
        return {"ok": False, "error": {"code": "bad_json", "message": f"{e}", "raw": out[-1]}}


def tool_call(_id: int, name: str, args: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return rpc({"jsonrpc": "2.0", "id": _id, "method": "tools/call", "params": {"name": name, "arguments": args or {}}})


def main() -> int:
    init = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"clientInfo": {"name": "smoke", "version": "0"}}})
    print("initialize:", init)

    tl = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    print("tools/list:", tl)

    # Always check ping
    print("ping:", tool_call(10, "frigg.ping", {}))

    # Bridge ping: if down, skip Blender tools
    bp = tool_call(11, "frigg.blender.bridge_ping", {})
    print("bridge_ping:", bp)

    if bp.get("result", {}).get("ok") is not True:
        print("[smoke] Bridge not available -> skipping Blender calls (run tools/frigg-bridge.ps1 to enable).")
        return 0

    # Blender calls (names must match tools/list)
    print("get_scene_info:", tool_call(12, "frigg.blender.get_scene_info", {}))
    print("list_objects:", tool_call(13, "frigg.blender.list_objects", {}))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
