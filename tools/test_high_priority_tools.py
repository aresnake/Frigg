"""
Test script for the 3 HIGH priority mesh editing tools.
Tests: bevel_edges, subdivide_mesh, recalculate_normals
"""

import json
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def bridge_call(method, params):
    """Send command to Blender bridge."""
    try:
        with socket.create_connection(("127.0.0.1", 8765), timeout=5) as sock:
            command = {"method": method, "params": params}
            sock.sendall((json.dumps(command) + "\n").encode())
            response = sock.makefile("r").readline()
            result = json.loads(response) if response else {"error": "No response"}

            if isinstance(result, dict) and result.get("ok"):
                return result["result"]
            elif isinstance(result, dict) and "error" in result:
                print(f"[ERROR] {result['error']}")
                return None
            return result
    except Exception as e:
        print(f"[ERROR] Bridge call failed: {e}")
        return None


def test_bevel_edges():
    """Test bevel_edges tool."""
    print("\n" + "="*60)
    print("TEST: bevel_edges")
    print("="*60)

    # Create test cube
    print("\n1. Creating test cube...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "BevelTest",
        "location": [0, 0, 0],
        "scale": 1
    })

    # Bevel all edges
    print("2. Beveling all edges...")
    result = bridge_call("bevel_edges", {
        "object_name": "BevelTest",
        "edge_indices": "all",
        "width": 0.1,
        "segments": 2,
        "profile": 0.5
    })

    if result:
        print(f"[OK] Beveled {len(result['beveled_edges'])} edges")
        print(f"     New vertex count: {result['new_vertex_count']}")
        return True
    else:
        print("[FAIL] bevel_edges failed")
        return False


def test_subdivide_mesh():
    """Test subdivide_mesh tool."""
    print("\n" + "="*60)
    print("TEST: subdivide_mesh")
    print("="*60)

    # Create test cube
    print("\n1. Creating test cube...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "SubdivideTest",
        "location": [3, 0, 0],
        "scale": 1
    })

    # Subdivide all faces
    print("2. Subdividing all faces...")
    result = bridge_call("subdivide_mesh", {
        "object_name": "SubdivideTest",
        "cuts": 2,
        "smooth": 0.5
    })

    if result:
        print(f"[OK] Subdivided {len(result['subdivided_faces'])} faces")
        print(f"     New vertex count: {result['new_vertex_count']}")
        print(f"     New face count: {result['new_face_count']}")
        return True
    else:
        print("[FAIL] subdivide_mesh failed")
        return False


def test_recalculate_normals():
    """Test recalculate_normals tool."""
    print("\n" + "="*60)
    print("TEST: recalculate_normals")
    print("="*60)

    # Create test cube
    print("\n1. Creating test cube...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "NormalsTest",
        "location": [6, 0, 0],
        "scale": 1
    })

    # Recalculate normals (outside)
    print("2. Recalculating normals (outside)...")
    result = bridge_call("recalculate_normals", {
        "object_name": "NormalsTest",
        "inside": False
    })

    if result:
        print(f"[OK] Normals recalculated: {result['status']}")
        print(f"     Face count: {result['face_count']}")
        return True
    else:
        print("[FAIL] recalculate_normals failed")
        return False


def main():
    """Run all high priority tool tests."""
    print("\n" + "="*60)
    print("FRIGG HIGH PRIORITY TOOLS TEST")
    print("Testing: bevel_edges, subdivide_mesh, recalculate_normals")
    print("="*60)

    # Check bridge connection
    result = bridge_call("bridge_ping", {})
    if not result:
        print("\n[ERROR] Bridge not connected!")
        print("Start the bridge: python tools/frigg_blender_bridge.py")
        return False

    print("[OK] Bridge connected")

    # Run tests
    tests = {
        "bevel_edges": test_bevel_edges,
        "subdivide_mesh": test_subdivide_mesh,
        "recalculate_normals": test_recalculate_normals,
    }

    results = {}
    for name, test_func in tests.items():
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test {name} crashed: {e}")
            results[name] = False

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results.items():
        status = "[OK] PASS" if passed else "[FAIL] FAIL"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

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
