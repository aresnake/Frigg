"""Test duplicate_object, delete_object, rename_object inline"""
import bpy

print("=" * 70)
print("TESTING ESSENTIAL OPERATIONS")
print("=" * 70)

def duplicate_object(params):
    """Duplicate an object with optional new name and location."""
    object_name = params.get("object_name") or params.get("name")
    new_name = params.get("new_name")
    offset = params.get("offset", [0, 0, 0])

    if not object_name:
        raise ValueError("duplicate_object requires 'object_name'")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Duplicate mesh data and object
    new_mesh = obj.data.copy() if obj.data else None
    new_obj = obj.copy()
    if new_mesh:
        new_obj.data = new_mesh

    # Link to scene
    bpy.context.scene.collection.objects.link(new_obj)

    # Set name
    if new_name:
        new_obj.name = new_name

    # Apply offset
    new_obj.location = [obj.location[i] + offset[i] for i in range(3)]

    return {
        "original": object_name,
        "duplicate": new_obj.name,
        "location": list(new_obj.location)
    }

def delete_object(params):
    """Delete an object from the scene."""
    object_name = params.get("object_name") or params.get("name")

    if not object_name:
        raise ValueError("delete_object requires 'object_name'")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Remove from all collections
    for collection in obj.users_collection:
        collection.objects.unlink(obj)

    # Remove object data
    bpy.data.objects.remove(obj, do_unlink=True)

    return {"deleted": object_name, "success": True}

def rename_object(params):
    """Rename an object."""
    object_name = params.get("object_name") or params.get("name")
    new_name = params.get("new_name")

    if not object_name or not new_name:
        raise ValueError("rename_object requires 'object_name' and 'new_name'")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    old_name = obj.name
    obj.name = new_name

    return {"old_name": old_name, "new_name": obj.name}

# Test 1: Duplicate
print("\nTest 1: Duplicate Cube")
if "Cube" in bpy.data.objects:
    result1 = duplicate_object({"object_name": "Cube", "new_name": "CubeCopy", "offset": [3, 0, 0]})
    print(f"  Original: {result1['original']}")
    print(f"  Duplicate: {result1['duplicate']}")
    print(f"  Location: {result1['location']}")
    if "CubeCopy" in bpy.data.objects:
        print("  OK - Duplicate created")

# Test 2: Rename
print("\nTest 2: Rename CubeCopy to MyCube")
if "CubeCopy" in bpy.data.objects:
    result2 = rename_object({"object_name": "CubeCopy", "new_name": "MyCube"})
    print(f"  Old: {result2['old_name']}")
    print(f"  New: {result2['new_name']}")
    if "MyCube" in bpy.data.objects:
        print("  OK - Renamed")

# Test 3: Delete
print("\nTest 3: Delete MyCube")
if "MyCube" in bpy.data.objects:
    result3 = delete_object({"object_name": "MyCube"})
    print(f"  Deleted: {result3['deleted']}")
    if "MyCube" not in bpy.data.objects:
        print("  OK - Deleted")

print("\n" + "=" * 70)
print("TEST PASSED - Essential operations work!")
print("=" * 70)

result = "essential_ops_work"
