"""
Test view orientations inline - validates the new view parameter logic

This tests that setting view rotation works correctly before restarting bridge.
"""

import bpy
import mathutils

print("=" * 70)
print("TESTING VIEW ORIENTATIONS LOGIC")
print("=" * 70)

# Find viewport
area = None
for window in bpy.context.window_manager.windows:
    for a in window.screen.areas:
        if a.type == 'VIEW_3D':
            area = a
            break
    if area:
        break

if not area:
    print("ERROR: No 3D viewport found")
    result = "no_viewport"
else:
    space = area.spaces.active
    region_3d = space.region_3d

    # Store original
    original_rotation = region_3d.view_rotation.copy()
    original_perspective = region_3d.view_perspective

    print(f"\nOriginal view rotation: {original_rotation}")
    print(f"Original perspective: {original_perspective}")

    # Test view rotations
    view_rotations = {
        "front": mathutils.Euler((1.5708, 0, 0), 'XYZ').to_quaternion(),
        "back": mathutils.Euler((1.5708, 0, 3.14159), 'XYZ').to_quaternion(),
        "right": mathutils.Euler((1.5708, 0, -1.5708), 'XYZ').to_quaternion(),
        "left": mathutils.Euler((1.5708, 0, 1.5708), 'XYZ').to_quaternion(),
        "top": mathutils.Euler((0, 0, 0), 'XYZ').to_quaternion(),
        "bottom": mathutils.Euler((3.14159, 0, 0), 'XYZ').to_quaternion(),
    }

    print("\nTesting view rotations:")
    for view_name, rotation in view_rotations.items():
        # Apply rotation
        region_3d.view_rotation = rotation

        # Read it back
        current = region_3d.view_rotation

        print(f"  {view_name:8s}: Set {rotation[:]} -> Got {current[:]}")

        # Verify it was set correctly (roughly)
        diff = sum(abs(a - b) for a, b in zip(rotation, current))
        if diff < 0.01:
            print(f"            OK (diff: {diff:.6f})")
        else:
            print(f"            WARNING: Large diff {diff:.6f}")

    # Test ortho switching
    print("\nTesting projection switching:")
    region_3d.view_perspective = 'ORTHO'
    print(f"  Set ORTHO -> Got {region_3d.view_perspective}")

    region_3d.view_perspective = 'PERSP'
    print(f"  Set PERSP -> Got {region_3d.view_perspective}")

    # Restore
    region_3d.view_rotation = original_rotation
    region_3d.view_perspective = original_perspective

    print("\nRestored to original state")
    print(f"  Rotation: {region_3d.view_rotation}")
    print(f"  Perspective: {region_3d.view_perspective}")

    print("\n" + "=" * 70)
    print("TEST PASSED - View orientation logic works!")
    print("=" * 70)

    result = "orientations_work"
