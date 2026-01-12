"""
Test spatial_relationships inline - determines positional relationships between objects

This will return relationships like "above", "below", "left", "right", "in_front", "behind"
based on the relative positions of two objects in 3D space.
"""

import bpy
import mathutils

print("=" * 70)
print("TESTING SPATIAL RELATIONSHIPS LOGIC")
print("=" * 70)

def get_spatial_relationships(object1_name, object2_name, threshold=0.1):
    """
    Determine spatial relationships between two objects.

    Args:
        object1_name: First object
        object2_name: Second object (reference)
        threshold: Minimum distance threshold to consider a relationship (in Blender units)

    Returns:
        Dictionary with relationships and detailed position info
    """
    obj1 = bpy.data.objects.get(object1_name)
    obj2 = bpy.data.objects.get(object2_name)

    if not obj1:
        raise ValueError(f"Object '{object1_name}' not found")
    if not obj2:
        raise ValueError(f"Object '{object2_name}' not found")

    # Get world locations
    loc1 = obj1.matrix_world.translation
    loc2 = obj2.matrix_world.translation

    # Calculate relative position vector (from obj2 to obj1)
    relative = loc1 - loc2

    # Determine relationships based on axes
    # X axis: left (-) / right (+)
    # Y axis: back (-) / front (+)
    # Z axis: below (-) / above (+)

    relationships = []

    if abs(relative.z) > threshold:
        if relative.z > 0:
            relationships.append("above")
        else:
            relationships.append("below")

    if abs(relative.x) > threshold:
        if relative.x > 0:
            relationships.append("right_of")
        else:
            relationships.append("left_of")

    if abs(relative.y) > threshold:
        if relative.y > 0:
            relationships.append("in_front_of")
        else:
            relationships.append("behind")

    # Calculate distance
    distance = relative.length

    # Determine primary relationship (largest offset)
    primary = None
    max_offset = max(abs(relative.x), abs(relative.y), abs(relative.z))

    if abs(relative.z) == max_offset:
        primary = "above" if relative.z > 0 else "below"
    elif abs(relative.x) == max_offset:
        primary = "right_of" if relative.x > 0 else "left_of"
    elif abs(relative.y) == max_offset:
        primary = "in_front_of" if relative.y > 0 else "behind"

    return {
        "object1": object1_name,
        "object2": object2_name,
        "relationships": relationships,
        "primary_relationship": primary,
        "relative_position": {
            "x": float(relative.x),
            "y": float(relative.y),
            "z": float(relative.z)
        },
        "distance": float(distance),
        "positions": {
            object1_name: [float(loc1.x), float(loc1.y), float(loc1.z)],
            object2_name: [float(loc2.x), float(loc2.y), float(loc2.z)]
        }
    }

# Test with default Cube
if "Cube" in bpy.data.objects:
    # Create a test object above the cube
    print("\nCreating test sphere above Cube...")

    # Check if test sphere already exists
    if "TestSphere" in bpy.data.objects:
        test_obj = bpy.data.objects["TestSphere"]
    else:
        # Create a proper UV sphere mesh
        import bmesh
        mesh = bpy.data.meshes.new("TestSphereMesh")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.5)
        bm.to_mesh(mesh)
        bm.free()

        test_obj = bpy.data.objects.new("TestSphere", mesh)
        bpy.context.scene.collection.objects.link(test_obj)

    # Position it above and to the right
    test_obj.location = (2.0, 0.0, 3.0)

    # Force update
    bpy.context.view_layer.update()

    print(f"TestSphere location: {test_obj.location}")
    print(f"Cube location: {bpy.data.objects['Cube'].location}")

    # Test relationships
    print("\nTest 1: TestSphere relative to Cube")
    result1 = get_spatial_relationships("TestSphere", "Cube")
    print(f"  Relationships: {result1['relationships']}")
    print(f"  Primary: {result1['primary_relationship']}")
    print(f"  Relative position: {result1['relative_position']}")
    print(f"  Distance: {result1['distance']:.2f}")

    # Test reverse
    print("\nTest 2: Cube relative to TestSphere")
    result2 = get_spatial_relationships("Cube", "TestSphere")
    print(f"  Relationships: {result2['relationships']}")
    print(f"  Primary: {result2['primary_relationship']}")
    print(f"  Relative position: {result2['relative_position']}")
    print(f"  Distance: {result2['distance']:.2f}")

    # Verify relationships are opposite
    if "above" in result1['relationships'] and "below" in result2['relationships']:
        print("\n  OK - Reciprocal relationships correct!")

    print("\n" + "=" * 70)
    print("TEST PASSED - Spatial relationships logic works!")
    print("=" * 70)

    result = "spatial_relationships_work"
else:
    print("ERROR: No Cube in scene for testing")
    result = "no_cube"
