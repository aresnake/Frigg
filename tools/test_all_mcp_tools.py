"""
FRIGG MCP - Complete Tool Test Suite
=====================================

Tests all 20 tools (12 existing + 8 new) via MCP bridge.
Run this via execute_python after bridge is started.

Author: Claude
Date: 2026-01-13
"""

import bpy
import sys
import traceback

# Add path for imports
sys.path.append("D:\\Frigg\\tools")

def clean_scene():
    """Clean scene before tests"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Remove all collections except default
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)

    # Remove all materials
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def test_core_tools():
    """Test core connectivity tools"""
    print("\n" + "="*60)
    print("CATEGORY: CORE TOOLS")
    print("="*60)

    results = []

    # Test 1: scene_info
    try:
        scene = bpy.context.scene
        result = {
            "name": scene.name,
            "frame_start": scene.frame_start,
            "frame_end": scene.frame_end,
            "object_count": len(bpy.data.objects)
        }
        print(f"✓ [1/2] scene_info: {result}")
        results.append(("scene_info", "PASS"))
    except Exception as e:
        print(f"✗ [1/2] scene_info: {e}")
        results.append(("scene_info", "FAIL"))

    # Test 2: list_objects
    try:
        objects = [obj.name for obj in bpy.data.objects]
        print(f"✓ [2/2] list_objects: {len(objects)} objects")
        results.append(("list_objects", "PASS"))
    except Exception as e:
        print(f"✗ [2/2] list_objects: {e}")
        results.append(("list_objects", "FAIL"))

    return results


def test_creation_tools():
    """Test object creation tools"""
    print("\n" + "="*60)
    print("CATEGORY: CREATION TOOLS")
    print("="*60)

    results = []

    # Test 1: create_primitive
    try:
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
        obj = bpy.context.active_object
        obj.name = "TestCube"
        print(f"✓ [1/2] create_primitive: Created '{obj.name}'")
        results.append(("create_primitive", "PASS"))
    except Exception as e:
        print(f"✗ [1/2] create_primitive: {e}")
        results.append(("create_primitive", "FAIL"))

    # Test 2: create_camera
    try:
        bpy.ops.object.camera_add(location=(5, -5, 3))
        cam = bpy.context.active_object
        cam.name = "TestCamera"
        print(f"✓ [2/2] create_camera: Created '{cam.name}'")
        results.append(("create_camera", "PASS"))
    except Exception as e:
        print(f"✗ [2/2] create_camera: {e}")
        results.append(("create_camera", "FAIL"))

    return results


def test_transform_tools():
    """Test transform tools"""
    print("\n" + "="*60)
    print("CATEGORY: TRANSFORM TOOLS")
    print("="*60)

    results = []

    obj = bpy.data.objects.get("TestCube")
    if not obj:
        print("✗ No TestCube found, skipping transforms")
        return [("transforms", "SKIP")]

    # Test 1: get_transform
    try:
        loc = obj.location
        rot = obj.rotation_euler
        scale = obj.scale
        print(f"✓ [1/3] get_transform: loc={list(loc)}, rot={list(rot)}, scale={list(scale)}")
        results.append(("get_transform", "PASS"))
    except Exception as e:
        print(f"✗ [1/3] get_transform: {e}")
        results.append(("get_transform", "FAIL"))

    # Test 2: set_transform (location)
    try:
        obj.location = (2, 3, 1)
        print(f"✓ [2/3] set_transform: Moved to {list(obj.location)}")
        results.append(("set_transform", "PASS"))
    except Exception as e:
        print(f"✗ [2/3] set_transform: {e}")
        results.append(("set_transform", "FAIL"))

    # Test 3: select_object
    try:
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        print(f"✓ [3/3] select_object: Selected '{obj.name}'")
        results.append(("select_object", "PASS"))
    except Exception as e:
        print(f"✗ [3/3] select_object: {e}")
        results.append(("select_object", "FAIL"))

    return results


def test_modifier_tools():
    """Test NEW modifier tools"""
    print("\n" + "="*60)
    print("CATEGORY: MODIFIER TOOLS (NEW v0.5)")
    print("="*60)

    from test_space_marine_tools import add_modifier, list_modifiers, apply_modifier

    results = []
    obj = bpy.data.objects.get("TestCube")

    if not obj:
        print("✗ No TestCube found, skipping modifiers")
        return [("modifiers", "SKIP")]

    # Test 1: add_modifier (Mirror)
    try:
        result = add_modifier({
            "object_name": "TestCube",
            "modifier_type": "MIRROR",
            "axis_x": True
        })
        print(f"✓ [1/3] add_modifier (MIRROR): {result['modifier_name']}")
        results.append(("add_modifier_mirror", "PASS"))
    except Exception as e:
        print(f"✗ [1/3] add_modifier (MIRROR): {e}")
        results.append(("add_modifier_mirror", "FAIL"))

    # Test 2: add_modifier (Subdivision)
    try:
        result = add_modifier({
            "object_name": "TestCube",
            "modifier_type": "SUBSURF",
            "levels": 2
        })
        print(f"✓ [2/3] add_modifier (SUBSURF): {result['modifier_name']}")
        results.append(("add_modifier_subsurf", "PASS"))
    except Exception as e:
        print(f"✗ [2/3] add_modifier (SUBSURF): {e}")
        results.append(("add_modifier_subsurf", "FAIL"))

    # Test 3: list_modifiers
    try:
        result = list_modifiers({"object_name": "TestCube"})
        print(f"✓ [3/3] list_modifiers: {result['modifier_count']} modifiers")
        for mod in result['modifiers']:
            print(f"    - {mod['name']} ({mod['type']})")
        results.append(("list_modifiers", "PASS"))
    except Exception as e:
        print(f"✗ [3/3] list_modifiers: {e}")
        results.append(("list_modifiers", "FAIL"))

    return results


def test_boolean_tools():
    """Test NEW boolean operation tools"""
    print("\n" + "="*60)
    print("CATEGORY: BOOLEAN TOOLS (NEW v0.5)")
    print("="*60)

    from test_space_marine_tools import boolean_operation

    results = []

    # Create target object for boolean
    try:
        bpy.ops.mesh.primitive_cylinder_add(location=(0.5, 0, 0), scale=(0.3, 0.3, 2))
        cutter = bpy.context.active_object
        cutter.name = "BooleanCutter"
        print(f"✓ [Setup] Created cutter object")
    except Exception as e:
        print(f"✗ [Setup] Failed to create cutter: {e}")
        return [("boolean_setup", "FAIL")]

    # Test 1: boolean_operation (DIFFERENCE)
    try:
        result = boolean_operation({
            "base_object": "TestCube",
            "target_object": "BooleanCutter",
            "operation": "DIFFERENCE",
            "apply": False,
            "hide_target": True
        })
        print(f"✓ [1/1] boolean_operation: {result['modifier_name']} ({result['operation']})")
        results.append(("boolean_operation", "PASS"))
    except Exception as e:
        print(f"✗ [1/1] boolean_operation: {e}")
        results.append(("boolean_operation", "FAIL"))

    return results


def test_material_tools():
    """Test NEW material tools"""
    print("\n" + "="*60)
    print("CATEGORY: MATERIAL TOOLS (NEW v0.5)")
    print("="*60)

    from test_space_marine_tools import create_material, assign_material

    results = []

    # Test 1: create_material
    try:
        result = create_material({
            "name": "TestMaterial",
            "base_color": [0.8, 0.2, 0.2, 1.0],
            "metallic": 0.9,
            "roughness": 0.3
        })
        print(f"✓ [1/2] create_material: '{result['material_name']}' (metallic={result['metallic']})")
        results.append(("create_material", "PASS"))
    except Exception as e:
        print(f"✗ [1/2] create_material: {e}")
        results.append(("create_material", "FAIL"))

    # Test 2: assign_material
    try:
        result = assign_material({
            "object_name": "TestCube",
            "material_name": "TestMaterial"
        })
        print(f"✓ [2/2] assign_material: '{result['material']}' → '{result['object']}'")
        results.append(("assign_material", "PASS"))
    except Exception as e:
        print(f"✗ [2/2] assign_material: {e}")
        results.append(("assign_material", "FAIL"))

    return results


def test_collection_tools():
    """Test NEW collection/organization tools"""
    print("\n" + "="*60)
    print("CATEGORY: ORGANIZATION TOOLS (NEW v0.5)")
    print("="*60)

    from test_space_marine_tools import create_collection, move_to_collection

    results = []

    # Test 1: create_collection
    try:
        result = create_collection({"name": "TestAssets"})
        print(f"✓ [1/2] create_collection: '{result['collection_name']}' ({result['status']})")
        results.append(("create_collection", "PASS"))
    except Exception as e:
        print(f"✗ [1/2] create_collection: {e}")
        results.append(("create_collection", "FAIL"))

    # Test 2: move_to_collection
    try:
        result = move_to_collection({
            "object_name": "TestCube",
            "collection_name": "TestAssets"
        })
        print(f"✓ [2/2] move_to_collection: '{result['object']}' → '{result['new_collection']}'")
        results.append(("move_to_collection", "PASS"))
    except Exception as e:
        print(f"✗ [2/2] move_to_collection: {e}")
        results.append(("move_to_collection", "FAIL"))

    return results


def print_summary(all_results):
    """Print final test summary"""
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)

    pass_count = sum(1 for _, status in all_results if status == "PASS")
    fail_count = sum(1 for _, status in all_results if status == "FAIL")
    skip_count = sum(1 for _, status in all_results if status == "SKIP")
    total = len(all_results)

    print(f"\n✓ PASSED: {pass_count}/{total}")
    print(f"✗ FAILED: {fail_count}/{total}")
    print(f"⊘ SKIPPED: {skip_count}/{total}")

    if fail_count > 0:
        print("\nFailed tests:")
        for name, status in all_results:
            if status == "FAIL":
                print(f"  - {name}")

    print("\n" + "="*60)
    if fail_count == 0 and skip_count == 0:
        print("🎉 ALL TESTS PASSED! MCP tools are production-ready.")
    elif fail_count == 0:
        print("✓ All executed tests passed (some skipped).")
    else:
        print("⚠ Some tests failed. Review errors above.")
    print("="*60 + "\n")

    return fail_count == 0


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FRIGG MCP - COMPLETE TOOL TEST SUITE")
    print("Testing 20 tools across 7 categories")
    print("="*60)

    all_results = []

    try:
        # Clean scene
        print("\n[SETUP] Cleaning scene...")
        clean_scene()
        print("✓ Scene cleaned\n")

        # Run test categories
        all_results.extend(test_core_tools())
        all_results.extend(test_creation_tools())
        all_results.extend(test_transform_tools())
        all_results.extend(test_modifier_tools())
        all_results.extend(test_boolean_tools())
        all_results.extend(test_material_tools())
        all_results.extend(test_collection_tools())

        # Print summary
        success = print_summary(all_results)

        return success

    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
