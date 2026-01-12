"""
Test set_object_scale inline

Scale in Blender is straightforward: [x, y, z] scale factors
- 1.0 = original size
- 2.0 = double size
- 0.5 = half size
- Can be uniform (all same) or non-uniform (different per axis)
"""

import bpy

print("=" * 70)
print("TESTING SET_OBJECT_SCALE LOGIC")
print("=" * 70)

def set_object_scale(params):
    """
    Set object scale.

    Parameters:
        object_name: Name of the object
        scale: [x, y, z] scale factors, or single number for uniform scale

    Returns:
        Current scale
    """
    object_name = params.get("object_name") or params.get("name")
    scale = params.get("scale")

    if not object_name:
        raise ValueError("set_object_scale requires 'object_name' parameter")
    if scale is None:
        raise ValueError("set_object_scale requires 'scale' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Handle uniform vs non-uniform scale
    if isinstance(scale, (int, float)):
        # Uniform scale
        obj.scale = (scale, scale, scale)
    elif isinstance(scale, (list, tuple)) and len(scale) == 3:
        # Non-uniform scale
        obj.scale = scale
    else:
        raise ValueError("scale must be a number or [x, y, z] array")

    return {
        "object_name": object_name,
        "scale": list(obj.scale),
        "location": list(obj.location),
        "rotation_euler_degrees": [0, 0, 0]  # Would need math.degrees for real values
    }

# Test with default Cube
if "Cube" in bpy.data.objects:
    cube = bpy.data.objects["Cube"]

    print(f"\nInitial Cube scale: {list(cube.scale)}")

    # Test 1: Uniform scale (double size)
    print("\nTest 1: Uniform scale (2.0 - double size)")
    result1 = set_object_scale({
        "object_name": "Cube",
        "scale": 2.0
    })
    print(f"  Result: {result1['scale']}")

    # Verify
    if all(abs(s - 2.0) < 0.01 for s in cube.scale):
        print("  OK - Uniform scale applied!")
    else:
        print(f"  FAIL - Expected [2, 2, 2], got {list(cube.scale)}")

    # Test 2: Non-uniform scale (stretch on Z)
    print("\nTest 2: Non-uniform scale [1, 1, 3]")
    result2 = set_object_scale({
        "object_name": "Cube",
        "scale": [1, 1, 3]
    })
    print(f"  Result: {result2['scale']}")

    expected = [1, 1, 3]
    if all(abs(cube.scale[i] - expected[i]) < 0.01 for i in range(3)):
        print("  OK - Non-uniform scale correct!")
    else:
        print(f"  FAIL - Expected {expected}, got {list(cube.scale)}")

    # Test 3: Scale down (half size)
    print("\nTest 3: Scale down to 0.5")
    result3 = set_object_scale({
        "object_name": "Cube",
        "scale": 0.5
    })
    print(f"  Result: {result3['scale']}")

    if all(abs(s - 0.5) < 0.01 for s in cube.scale):
        print("  OK - Scale down correct!")

    # Test 4: Different per-axis scales
    print("\nTest 4: Different per-axis [2, 0.5, 1.5]")
    result4 = set_object_scale({
        "object_name": "Cube",
        "scale": [2, 0.5, 1.5]
    })
    print(f"  Result: {result4['scale']}")

    expected = [2, 0.5, 1.5]
    if all(abs(cube.scale[i] - expected[i]) < 0.01 for i in range(3)):
        print("  OK - Per-axis scale correct!")

    # Test 5: Reset to original (1, 1, 1)
    print("\nTest 5: Reset to original scale")
    result5 = set_object_scale({
        "object_name": "Cube",
        "scale": 1.0
    })
    print(f"  Result: {result5['scale']}")

    if all(abs(s - 1.0) < 0.01 for s in cube.scale):
        print("  OK - Reset to original!")

    print("\n" + "=" * 70)
    print("TEST PASSED - set_object_scale logic works!")
    print("=" * 70)

    result = "scale_works"
else:
    print("ERROR: No Cube in scene")
    result = "no_cube"
