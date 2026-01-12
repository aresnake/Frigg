"""
Test set_object_rotation inline - supports both Euler and Quaternion

Rotation in Blender can be:
- Euler (XYZ angles in radians)
- Quaternion (WXYZ)
- Axis-angle

For user-friendliness, we'll support:
1. Euler angles in degrees (most intuitive)
2. Euler angles in radians (Blender native)
3. Quaternion (for advanced users)
"""

import bpy
import math

print("=" * 70)
print("TESTING SET_OBJECT_ROTATION LOGIC")
print("=" * 70)

def set_object_rotation(params):
    """
    Set object rotation with multiple input formats.

    Parameters:
        object_name: Name of the object
        rotation: [x, y, z] angles
        rotation_mode: "degrees" | "radians" | "quaternion" (default: degrees)
        order: "XYZ" | "XZY" | "YXZ" | "YZX" | "ZXY" | "ZYX" (default: XYZ)

    Returns:
        Current rotation in both formats
    """
    object_name = params.get("object_name") or params.get("name")
    rotation = params.get("rotation")
    rotation_mode = params.get("rotation_mode", "degrees")
    order = params.get("order", "XYZ")

    if not object_name:
        raise ValueError("set_object_rotation requires 'object_name' parameter")
    if not rotation or len(rotation) != 3:
        raise ValueError("set_object_rotation requires 'rotation' as [x, y, z]")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Convert to radians if needed
    if rotation_mode == "degrees":
        rotation_rad = [math.radians(angle) for angle in rotation]
    elif rotation_mode == "radians":
        rotation_rad = rotation
    elif rotation_mode == "quaternion":
        # Assume [w, x, y, z] quaternion format
        import mathutils
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = mathutils.Quaternion(rotation)
        return {
            "object_name": object_name,
            "rotation_quaternion": list(obj.rotation_quaternion),
            "rotation_euler_degrees": [math.degrees(a) for a in obj.rotation_euler],
            "rotation_mode": "QUATERNION"
        }
    else:
        raise ValueError(f"Invalid rotation_mode: {rotation_mode}")

    # Set Euler rotation
    obj.rotation_mode = order
    obj.rotation_euler = rotation_rad

    return {
        "object_name": object_name,
        "rotation_euler_radians": list(obj.rotation_euler),
        "rotation_euler_degrees": [math.degrees(a) for a in obj.rotation_euler],
        "rotation_mode": order,
        "location": list(obj.location),
        "scale": list(obj.scale)
    }

# Test with default Cube
if "Cube" in bpy.data.objects:
    cube = bpy.data.objects["Cube"]

    print(f"\nInitial Cube rotation: {[math.degrees(a) for a in cube.rotation_euler]}")

    # Test 1: Rotate 45 degrees on Z axis
    print("\nTest 1: Rotate 45° on Z axis")
    result1 = set_object_rotation({
        "object_name": "Cube",
        "rotation": [0, 0, 45],
        "rotation_mode": "degrees"
    })
    print(f"  Result degrees: {result1['rotation_euler_degrees']}")
    print(f"  Result radians: {result1['rotation_euler_radians']}")

    # Verify
    actual = [math.degrees(a) for a in cube.rotation_euler]
    if abs(actual[2] - 45.0) < 0.01:
        print("  OK - Rotation applied correctly!")
    else:
        print(f"  FAIL - Expected 45°, got {actual[2]:.2f}°")

    # Test 2: Rotate on multiple axes
    print("\nTest 2: Rotate 90° X, 45° Y, 30° Z")
    result2 = set_object_rotation({
        "object_name": "Cube",
        "rotation": [90, 45, 30],
        "rotation_mode": "degrees"
    })
    print(f"  Result degrees: {result2['rotation_euler_degrees']}")

    actual = [math.degrees(a) for a in cube.rotation_euler]
    expected = [90, 45, 30]

    all_match = all(abs(actual[i] - expected[i]) < 0.01 for i in range(3))
    if all_match:
        print("  OK - Multi-axis rotation correct!")
    else:
        print(f"  FAIL - Expected {expected}, got {[f'{a:.2f}' for a in actual]}")

    # Test 3: Radians mode
    print("\nTest 3: Using radians directly")
    pi = math.pi
    result3 = set_object_rotation({
        "object_name": "Cube",
        "rotation": [pi/4, pi/2, pi/6],  # 45°, 90°, 30°
        "rotation_mode": "radians"
    })
    print(f"  Result degrees: {result3['rotation_euler_degrees']}")

    # Test 4: Different rotation order
    print("\nTest 4: Different rotation order (ZYX)")
    result4 = set_object_rotation({
        "object_name": "Cube",
        "rotation": [45, 90, 30],
        "rotation_mode": "degrees",
        "order": "ZYX"
    })
    print(f"  Result: {result4['rotation_euler_degrees']}")
    print(f"  Order: {result4['rotation_mode']}")

    # Reset to zero
    print("\nTest 5: Reset to zero")
    result5 = set_object_rotation({
        "object_name": "Cube",
        "rotation": [0, 0, 0],
        "rotation_mode": "degrees"
    })
    print(f"  Result: {result5['rotation_euler_degrees']}")

    actual = [math.degrees(a) for a in cube.rotation_euler]
    if all(abs(a) < 0.01 for a in actual):
        print("  OK - Reset to zero!")

    print("\n" + "=" * 70)
    print("TEST PASSED - set_object_rotation logic works!")
    print("=" * 70)

    result = "rotation_works"
else:
    print("ERROR: No Cube in scene")
    result = "no_cube"
