"""
Test bounding box calculation inline before integration
"""

import bpy

print("=" * 70)
print("TESTING BOUNDING BOX CALCULATION")
print("=" * 70)

# Get the default Cube (should exist in new scene)
obj_name = "Cube"
obj = bpy.data.objects.get(obj_name)

if not obj:
    print(f"ERROR: Object '{obj_name}' not found")
    result = "no_object"
else:
    print(f"\nObject: {obj.name}")
    print(f"  Type: {obj.type}")
    print(f"  Location: {obj.location}")
    print(f"  Scale: {obj.scale}")

    # Get bounding box in local space
    if hasattr(obj, 'bound_box'):
        bbox_local = obj.bound_box
        print(f"\n  Local bounding box (8 corners):")
        for i, corner in enumerate(bbox_local):
            print(f"    Corner {i}: {corner}")

        # Calculate dimensions in local space
        import mathutils
        min_local = mathutils.Vector((
            min(corner[0] for corner in bbox_local),
            min(corner[1] for corner in bbox_local),
            min(corner[2] for corner in bbox_local)
        ))
        max_local = mathutils.Vector((
            max(corner[0] for corner in bbox_local),
            max(corner[1] for corner in bbox_local),
            max(corner[2] for corner in bbox_local)
        ))
        dimensions_local = max_local - min_local

        print(f"\n  Local dimensions: {dimensions_local}")

        # Get world space bounding box
        matrix_world = obj.matrix_world
        bbox_world = [matrix_world @ mathutils.Vector(corner) for corner in bbox_local]

        print(f"\n  World bounding box (8 corners):")
        for i, corner in enumerate(bbox_world):
            print(f"    Corner {i}: ({corner.x:.3f}, {corner.y:.3f}, {corner.z:.3f})")

        # Calculate dimensions in world space
        min_world = mathutils.Vector((
            min(corner.x for corner in bbox_world),
            min(corner.y for corner in bbox_world),
            min(corner.z for corner in bbox_world)
        ))
        max_world = mathutils.Vector((
            max(corner.x for corner in bbox_world),
            max(corner.y for corner in bbox_world),
            max(corner.z for corner in bbox_world)
        ))
        dimensions_world = max_world - min_world
        center_world = (min_world + max_world) / 2

        print(f"\n  World min: ({min_world.x:.3f}, {min_world.y:.3f}, {min_world.z:.3f})")
        print(f"  World max: ({max_world.x:.3f}, {max_world.y:.3f}, {max_world.z:.3f})")
        print(f"  World center: ({center_world.x:.3f}, {center_world.y:.3f}, {center_world.z:.3f})")
        print(f"  World dimensions: ({dimensions_world.x:.3f}, {dimensions_world.y:.3f}, {dimensions_world.z:.3f})")

        # Calculate volume
        volume = dimensions_world.x * dimensions_world.y * dimensions_world.z
        print(f"\n  Volume: {volume:.3f} cubic units")

        print("\n" + "=" * 70)
        print("TEST PASSED - Bounding box calculation works!")
        print("=" * 70)

        result = "bounding_box_works"
    else:
        print(f"ERROR: Object has no bound_box attribute")
        result = "no_bbox"
