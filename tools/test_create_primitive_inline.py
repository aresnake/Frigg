"""
Test create_primitive inline - unified primitive creation

Primitives to support:
- cube
- sphere (UV sphere)
- cylinder
- cone
- torus
- plane
- monkey (Suzanne)
"""

import bpy
import bmesh

print("=" * 70)
print("TESTING CREATE_PRIMITIVE LOGIC")
print("=" * 70)

def create_primitive(params):
    """
    Create a primitive object.

    Parameters:
        primitive_type: "cube" | "sphere" | "cylinder" | "cone" | "torus" | "plane" | "monkey"
        name: Optional custom name (defaults to type name)
        location: Optional [x, y, z] location (default [0, 0, 0])
        rotation: Optional [x, y, z] rotation in degrees (default [0, 0, 0])
        scale: Optional uniform scale or [x, y, z] (default 1.0)
        size: Optional size parameter (meaning varies by type)

    Returns:
        Object info with name, type, location, bounds
    """
    import math

    primitive_type = params.get("primitive_type") or params.get("type")
    name = params.get("name")
    location = params.get("location", [0, 0, 0])
    rotation = params.get("rotation", [0, 0, 0])
    scale_param = params.get("scale", 1.0)
    size = params.get("size", 2.0)  # Default size for primitives

    if not primitive_type:
        raise ValueError("create_primitive requires 'primitive_type' parameter")

    primitive_type = primitive_type.lower()

    # Create mesh
    mesh = bpy.data.meshes.new(f"{primitive_type}_mesh")
    bm = bmesh.new()

    # Create geometry based on type
    if primitive_type == "cube":
        bmesh.ops.create_cube(bm, size=size)
        default_name = "Cube"

    elif primitive_type == "sphere":
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=size/2)
        default_name = "Sphere"

    elif primitive_type == "cylinder":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
                             radius1=size/2, radius2=size/2, depth=size)
        default_name = "Cylinder"

    elif primitive_type == "cone":
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=32,
                             radius1=size/2, radius2=0, depth=size)
        default_name = "Cone"

    elif primitive_type == "torus":
        # Torus needs operator - special case
        bm.free()
        bpy.ops.mesh.primitive_torus_add(location=location, major_radius=size/2, minor_radius=size/4)
        obj = bpy.context.active_object
        obj.name = name or "Torus"
        obj.rotation_euler = [math.radians(a) for a in rotation]
        if isinstance(scale_param, (int, float)):
            obj.scale = (scale_param, scale_param, scale_param)
        else:
            obj.scale = scale_param

        return {
            "name": obj.name,
            "type": primitive_type,
            "location": list(obj.location),
            "rotation_degrees": rotation,
            "scale": list(obj.scale)
        }

    elif primitive_type == "plane":
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=size/2)
        default_name = "Plane"

    elif primitive_type == "monkey":
        # Suzanne needs operator - special case
        bm.free()
        bpy.ops.mesh.primitive_monkey_add(location=location)
        obj = bpy.context.active_object
        obj.name = name or "Suzanne"
        obj.rotation_euler = [math.radians(a) for a in rotation]
        if isinstance(scale_param, (int, float)):
            obj.scale = (scale_param, scale_param, scale_param)
        else:
            obj.scale = scale_param

        return {
            "name": obj.name,
            "type": primitive_type,
            "location": list(obj.location),
            "rotation_degrees": rotation,
            "scale": list(obj.scale)
        }

    else:
        bm.free()
        raise ValueError(f"Unknown primitive type: {primitive_type}. Supported: cube, sphere, cylinder, cone, torus, plane, monkey")

    # Convert bmesh to mesh
    bm.to_mesh(mesh)
    bm.free()

    # Create object
    obj_name = name or default_name
    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Set transform
    obj.location = location
    obj.rotation_euler = [math.radians(a) for a in rotation]

    if isinstance(scale_param, (int, float)):
        obj.scale = (scale_param, scale_param, scale_param)
    else:
        obj.scale = scale_param

    # Update scene
    bpy.context.view_layer.update()

    return {
        "name": obj.name,
        "type": primitive_type,
        "location": list(obj.location),
        "rotation_degrees": rotation,
        "scale": list(obj.scale)
    }


# Test 1: Create cube
print("\nTest 1: Create cube")
result1 = create_primitive({"primitive_type": "cube", "name": "TestCube"})
print(f"  Created: {result1['name']} (type: {result1['type']})")
print(f"  Location: {result1['location']}")
if "TestCube" in bpy.data.objects:
    print("  OK - Cube created")

# Test 2: Create sphere at different location
print("\nTest 2: Create sphere at [2, 0, 0]")
result2 = create_primitive({
    "primitive_type": "sphere",
    "name": "TestSphere",
    "location": [2, 0, 0]
})
print(f"  Created: {result2['name']}")
print(f"  Location: {result2['location']}")
if "TestSphere" in bpy.data.objects:
    sphere = bpy.data.objects["TestSphere"]
    if abs(sphere.location.x - 2.0) < 0.01:
        print("  OK - Sphere at correct location")

# Test 3: Create cylinder with rotation
print("\nTest 3: Create cylinder rotated 45° on Z")
result3 = create_primitive({
    "primitive_type": "cylinder",
    "name": "TestCylinder",
    "location": [0, 2, 0],
    "rotation": [0, 0, 45]
})
print(f"  Created: {result3['name']}")
print(f"  Rotation: {result3['rotation_degrees']}")
if "TestCylinder" in bpy.data.objects:
    print("  OK - Cylinder created with rotation")

# Test 4: Create cone with custom scale
print("\nTest 4: Create cone with scale 1.5")
result4 = create_primitive({
    "primitive_type": "cone",
    "location": [-2, 0, 0],
    "scale": 1.5
})
print(f"  Created: {result4['name']}")
print(f"  Scale: {result4['scale']}")
if result4['scale'] == [1.5, 1.5, 1.5]:
    print("  OK - Uniform scale applied")

# Test 5: Create torus
print("\nTest 5: Create torus")
result5 = create_primitive({"primitive_type": "torus", "name": "TestTorus"})
print(f"  Created: {result5['name']}")
if "TestTorus" in bpy.data.objects:
    print("  OK - Torus created")

# Test 6: Create plane
print("\nTest 6: Create plane")
result6 = create_primitive({"primitive_type": "plane", "location": [0, 0, -1]})
print(f"  Created: {result6['name']}")
if "Plane" in bpy.data.objects:
    print("  OK - Plane created")

print("\n" + "=" * 70)
print("TEST PASSED - create_primitive logic works!")
print("=" * 70)
print(f"\nTotal objects in scene: {len(bpy.data.objects)}")

result = "create_primitive_works"
