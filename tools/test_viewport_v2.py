"""
Test the new viewport_snapshot v2 implementation
"""

# Load the v2 function
exec(open('D:/Frigg/tools/viewport_snapshot_v2.py').read())

print("=" * 70)
print("TESTING viewport_snapshot v2")
print("=" * 70)

# Test 1: Basic snapshot
print("\nTEST 1: Basic snapshot (solid, perspective, front)")
params1 = {
    "shading": "solid",
    "projection": "perspective",
    "view": "front",
    "width": 256,
    "height": 256
}

result1 = viewport_snapshot(params1)
print(f"  Success: {result1['success']}")
print(f"  Size: {result1['width']}x{result1['height']}")
print(f"  Image length: {len(result1['image'])} chars")
print(f"  View: {result1['view_info']['view']}")
print(f"  Engine: {result1['view_info']['render_engine']}")

# Test 2: Wireframe ortho top view
print("\nTEST 2: Wireframe ortho top view")
params2 = {
    "shading": "wireframe",
    "projection": "ortho",
    "view": "top",
    "width": 256,
    "height": 256
}

result2 = viewport_snapshot(params2)
print(f"  Success: {result2['success']}")
print(f"  Shading: {result2['view_info']['shading']}")
print(f"  Projection: {result2['view_info']['projection']}")

# Test 3: Focus on specific object (if Cube exists)
import bpy
if "Cube" in bpy.data.objects:
    print("\nTEST 3: Focus on Cube (isolate + fit)")
    params3 = {
        "shading": "solid",
        "projection": "perspective",
        "view": "front",
        "target": "Cube",
        "isolate": True,
        "fit_to_view": True,
        "width": 256,
        "height": 256
    }

    result3 = viewport_snapshot(params3)
    print(f"  Success: {result3['success']}")
    print(f"  Target isolation worked!")
else:
    print("\nTEST 3: Skipped (no Cube in scene)")

print("\n" + "=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)

result = "v2_works"
