"""
Test script for the 4 new mesh editing tools.
Run this from command line: python tools/test_mesh_editing.py
"""

import json
import socket
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def send_bridge_command(method, params):
    """Send command to Blender bridge via socket."""
    try:
        with socket.create_connection(("127.0.0.1", 8765), timeout=5) as sock:
            command = {"method": method, "params": params}
            sock.sendall((json.dumps(command) + "\n").encode())
            response = sock.makefile("r").readline()
            return json.loads(response) if response else {"error": "No response"}
    except ConnectionRefusedError:
        return {"error": "Blender bridge not running on port 8765"}
    except Exception as e:
        return {"error": str(e)}


def test_tool(tool_name, method, params):
    """Test a single tool."""
    print(f"\n{'='*60}")
    print(f"Testing: {tool_name}")
    print(f"{'='*60}")
    print(f"Method: {method}")
    print(f"Params: {json.dumps(params, indent=2)}")

    result = send_bridge_command(method, params)

    print(f"\nResult:")
    print(json.dumps(result, indent=2, default=str))

    # Check for both error in response and ok: False
    if "error" in result or (isinstance(result, dict) and result.get("ok") == False):
        error_msg = result.get("error", "Unknown error")
        print(f"\n[FAIL] FAILED: {error_msg}")
        return False

    print(f"\n[OK] SUCCESS")
    return True


def main():
    print("\n" + "="*60)
    print("MESH EDITING TOOLS TEST")
    print("="*60)

    # Check bridge connectivity
    print("\nChecking Blender bridge...")
    ping = send_bridge_command("bridge_ping", {})
    if "error" in ping:
        print(f"[FAIL] Bridge not available: {ping['error']}")
        print("Please start Blender with the bridge addon enabled.")
        return False
    print(f"[OK] Bridge connected: {ping}")

    results = {}

    # Test 1: Join objects
    print("\n\n" + "="*60)
    print("TEST 1: Join Objects")
    print("="*60)
    print("Setup: Creating two cubes...")
    send_bridge_command("create_primitive", {"primitive_type": "cube", "name": "JoinCube1", "location": [0, 0, 0]})
    send_bridge_command("create_primitive", {"primitive_type": "cube", "name": "JoinCube2", "location": [2, 0, 0]})

    results["join_objects"] = test_tool(
        "frigg_blender_join_objects",
        "join_objects",
        {"object_names": ["JoinCube1", "JoinCube2"], "result_name": "JoinedMesh"}
    )

    # Test 2: Extrude faces
    print("\n\n" + "="*60)
    print("TEST 2: Extrude Faces")
    print("="*60)
    print("Setup: Creating a cube...")
    send_bridge_command("create_primitive", {"primitive_type": "cube", "name": "ExtrudeCube", "location": [0, 3, 0]})

    results["extrude_faces"] = test_tool(
        "frigg_blender_extrude_faces",
        "extrude_faces",
        {"object_name": "ExtrudeCube", "face_indices": [5], "offset": 0.5}
    )

    # Test 3: Inset faces
    print("\n\n" + "="*60)
    print("TEST 3: Inset Faces")
    print("="*60)
    print("Setup: Creating a cube...")
    send_bridge_command("create_primitive", {"primitive_type": "cube", "name": "InsetCube", "location": [0, 6, 0]})

    results["inset_faces"] = test_tool(
        "frigg_blender_inset_faces",
        "inset_faces",
        {"object_name": "InsetCube", "thickness": 0.1, "depth": 0.0}
    )

    # Test 4: Merge vertices
    print("\n\n" + "="*60)
    print("TEST 4: Merge Vertices")
    print("="*60)

    results["merge_vertices"] = test_tool(
        "frigg_blender_merge_vertices",
        "merge_vertices",
        {"object_name": "InsetCube", "distance": 0.001}
    )

    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    for tool_name, success in results.items():
        status = "[OK] PASS" if success else "[FAIL] FAIL"
        print(f"{tool_name}: {status}")

    print(f"\nTotal: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n[OK][OK][OK] ALL TESTS PASSED!")
        return True
    else:
        print(f"\n[FAIL] {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
