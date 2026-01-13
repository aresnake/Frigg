#!/usr/bin/env python3
"""
Test script to verify that all MCP tools work correctly after bug fixes.
"""

import socket
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from frigg_mcp.tools import core_tools


def get_bridge_port():
    """Read bridge port from state file"""
    state_file = os.path.join(os.path.dirname(__file__), '..', '.frigg_bridge.json')
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            return state.get('host', '127.0.0.1'), state.get('port', 8765)
    except:
        return '127.0.0.1', 8765


def call_bridge(method: str, params: dict):
    """Call the Blender bridge"""
    host, port = get_bridge_port()
    request = {"method": method, "params": params}
    data = json.dumps(request) + "\n"

    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall(data.encode("utf-8"))
            file = sock.makefile("r", encoding="utf-8")
            line = file.readline()
            if not line:
                return {"ok": False, "error": "Empty response"}
            return json.loads(line)
    except Exception as e:
        return {"ok": False, "error": str(e)}


def test_tool(name, arguments=None):
    """Test a single tool"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Arguments: {arguments}")
    print(f"{'='*60}")

    try:
        result = core_tools.handle_core_call(name, arguments, call_bridge)

        if result.get("ok"):
            print("[OK] SUCCESS")
            print(f"Result: {json.dumps(result.get('result'), indent=2)}")
            return True
        else:
            print("[FAIL] FAILED")
            print(f"Error: {result.get('error')}")
            return False
    except Exception as e:
        print(f"[FAIL] EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FRIGG MCP TOOL TEST SUITE")
    print("="*60)

    # Check tool name format
    print("\nChecking tool name format...")
    import re
    pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')

    invalid_names = []
    for tool_def in core_tools.CORE_TOOL_DEFS:
        name = tool_def["name"]
        if not pattern.match(name):
            invalid_names.append(name)
            print(f"  [FAIL] Invalid name: {name}")
        else:
            print(f"  [OK] Valid name: {name}")

    if invalid_names:
        print(f"\n[FAIL] {len(invalid_names)} tools have invalid names!")
        return 1
    else:
        print(f"\n[OK] All {len(core_tools.CORE_TOOL_DEFS)} tool names are valid!")

    # Test basic tools
    tests = [
        ("frigg_ping", None),
        ("frigg_blender_bridge_ping", None),
        ("frigg_blender_get_scene_info", None),
        ("frigg_blender_list_objects", None),
        ("frigg_blender_get_transform", {"name": "Cube"}),
    ]

    passed = 0
    failed = 0

    for test_name, test_args in tests:
        if test_tool(test_name, test_args):
            passed += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"[OK] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"Total: {passed + failed}")

    if failed == 0:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n[WARNING]  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
