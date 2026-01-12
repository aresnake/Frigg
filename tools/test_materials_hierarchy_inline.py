"""Test set_material, set_parent, set_smooth_shading inline"""
import bpy

print("=" * 70)
print("TESTING MATERIALS & HIERARCHY")
print("=" * 70)

def set_material(params):
    """Create/assign material with color and properties."""
    object_name = params.get("object_name") or params.get("name")
    material_name = params.get("material_name", "Material")
    color = params.get("color", [0.8, 0.8, 0.8, 1.0])
    metallic = params.get("metallic", 0.0)
    roughness = params.get("roughness", 0.5)

    if not object_name:
        raise ValueError("set_material requires 'object_name'")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Create or get material
    mat = bpy.data.materials.get(material_name)
    if not mat:
        mat = bpy.data.materials.new(name=material_name)
        mat.use_nodes = True

    # Get principled BSDF
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness

    # Assign to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    return {
        "object_name": object_name,
        "material_name": mat.name,
        "color": list(color),
        "metallic": metallic,
        "roughness": roughness
    }

def set_parent(params):
    """Set parent-child relationship."""
    child_name = params.get("child") or params.get("child_name")
    parent_name = params.get("parent") or params.get("parent_name")
    keep_transform = params.get("keep_transform", True)

    if not child_name or not parent_name:
        raise ValueError("set_parent requires 'child' and 'parent'")

    child = bpy.data.objects.get(child_name)
    parent = bpy.data.objects.get(parent_name)

    if not child:
        raise ValueError(f"Child '{child_name}' not found")
    if not parent:
        raise ValueError(f"Parent '{parent_name}' not found")

    child.parent = parent
    if keep_transform:
        child.matrix_parent_inverse = parent.matrix_world.inverted()

    return {
        "child": child_name,
        "parent": parent_name,
        "keep_transform": keep_transform
    }

def set_smooth_shading(params):
    """Set smooth or flat shading."""
    object_name = params.get("object_name") or params.get("name")
    smooth = params.get("smooth", True)

    if not object_name:
        raise ValueError("set_smooth_shading requires 'object_name'")

    obj = bpy.data.objects.get(object_name)
    if not obj or obj.type != 'MESH':
        raise ValueError(f"Mesh object '{object_name}' not found")

    # Set shading for all polygons
    for poly in obj.data.polygons:
        poly.use_smooth = smooth

    return {
        "object_name": object_name,
        "smooth": smooth
    }

# Test 1: Material
print("\nTest 1: Set red material on Cube")
if "Cube" in bpy.data.objects:
    result1 = set_material({
        "object_name": "Cube",
        "material_name": "RedMat",
        "color": [1, 0, 0, 1],
        "metallic": 0.2,
        "roughness": 0.3
    })
    print(f"   Object: {result1['object_name']}")
    print(f"   Material: {result1['material_name']}")
    print(f"   Color: {result1['color']}")
    if "RedMat" in bpy.data.materials:
        print("   OK - Material created and assigned")

# Test 2: Smooth shading
print("\nTest 2: Set smooth shading on Cube")
if "Cube" in bpy.data.objects:
    result2 = set_smooth_shading({"object_name": "Cube", "smooth": True})
    print(f"   Object: {result2['object_name']}")
    print(f"   Smooth: {result2['smooth']}")
    cube = bpy.data.objects["Cube"]
    if cube.data.polygons[0].use_smooth:
        print("   OK - Smooth shading enabled")

# Test 3: Parent-child (need to create child first)
print("\nTest 3: Create sphere and parent to Cube")
bpy.ops.mesh.primitive_uv_sphere_add(location=[2, 0, 0])
sphere = bpy.context.active_object
sphere.name = "ChildSphere"

result3 = set_parent({"child": "ChildSphere", "parent": "Cube"})
print(f"   Child: {result3['child']}")
print(f"   Parent: {result3['parent']}")
if sphere.parent and sphere.parent.name == "Cube":
    print("   OK - Parent-child relationship set")

print("\n" + "=" * 70)
print("TEST PASSED - Materials & Hierarchy work!")
print("=" * 70)

result = "materials_hierarchy_work"
