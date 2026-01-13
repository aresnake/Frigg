"""
Test des bridge handlers via le système de commandes
À exécuter dans Blender Python console
"""

import json
import sys
import os

# Ajouter le chemin du bridge addon
BRIDGE_PATH = r"D:\Frigg\blender_bridge_addon"
if BRIDGE_PATH not in sys.path:
    sys.path.insert(0, BRIDGE_PATH)

import bpy

# Importer les handlers depuis le bridge addon
try:
    # Recharger le module si déjà chargé
    if "__init__" in sys.modules:
        import importlib
        importlib.reload(sys.modules["__init__"])

    # Importer depuis le nom du package si c'est un addon installé
    from blender_bridge_addon import COMMAND_HANDLERS
except:
    # Sinon importer directement
    try:
        import __init__ as bridge_module
        COMMAND_HANDLERS = bridge_module.COMMAND_HANDLERS
    except Exception as e:
        print(f"❌ Failed to import COMMAND_HANDLERS: {e}")
        print("Make sure blender_bridge_addon is installed or path is correct")
        COMMAND_HANDLERS = {}

def test_handler(handler_name, command_data):
    """Tester un handler spécifique"""
    print(f"\n{'='*60}")
    print(f"Testing handler: {handler_name}")
    print(f"{'='*60}")
    print(f"Input: {json.dumps(command_data, indent=2)}")

    if handler_name not in COMMAND_HANDLERS:
        print(f"❌ Handler '{handler_name}' not found in COMMAND_HANDLERS!")
        print(f"Available handlers: {list(COMMAND_HANDLERS.keys())}")
        return False

    handler = COMMAND_HANDLERS[handler_name]

    try:
        result = handler(command_data)
        print(f"\nResult: {json.dumps(result, indent=2, default=str)}")

        if "error" in result:
            print(f"\n❌ Handler returned error: {result['error']}")
            return False

        print("\n✅ Handler executed successfully")
        return True

    except Exception as e:
        print(f"\n❌ Exception raised: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# TESTS POUR BATCH 1 : MESH EDITING
# =============================================================================

def test_batch_1_mesh_editing():
    """Test handlers for mesh editing tools"""
    print("\n" + "="*60)
    print("BATCH 1: MESH EDITING HANDLERS")
    print("="*60)

    all_passed = True

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Test 1: join_objects
    print("\n--- Test 1: join_objects ---")
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube1 = bpy.context.active_object
    cube1.name = "Cube1"

    bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
    cube2 = bpy.context.active_object
    cube2.name = "Cube2"

    if not test_handler("join_objects", {
        "object_names": ["Cube1", "Cube2"],
        "result_name": "JoinedCubes"
    }):
        all_passed = False

    # Test 2: extrude_faces
    print("\n--- Test 2: extrude_faces ---")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    if not test_handler("extrude_faces", {
        "object_name": "TestCube",
        "face_indices": [5],  # Top face
        "offset": 0.5
    }):
        all_passed = False

    # Test 3: inset_faces
    print("\n--- Test 3: inset_faces ---")
    if not test_handler("inset_faces", {
        "object_name": "TestCube",
        "thickness": 0.1,
        "depth": 0.0
    }):
        all_passed = False

    # Test 4: merge_vertices
    print("\n--- Test 4: merge_vertices ---")
    if not test_handler("merge_vertices", {
        "object_name": "TestCube",
        "distance": 0.001
    }):
        all_passed = False

    return all_passed

# =============================================================================
# TESTS POUR BATCH 2 : EDGE OPERATIONS
# =============================================================================

def test_batch_2_edge_operations():
    """Test handlers for edge operations"""
    print("\n" + "="*60)
    print("BATCH 2: EDGE OPERATIONS HANDLERS")
    print("="*60)

    all_passed = True

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Test 1: bevel_edges
    print("\n--- Test 1: bevel_edges ---")
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    if not test_handler("bevel_edges", {
        "object_name": "TestCube",
        "width": 0.1,
        "segments": 2
    }):
        all_passed = False

    # Test 2: subdivide_mesh
    print("\n--- Test 2: subdivide_mesh ---")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    if not test_handler("subdivide_mesh", {
        "object_name": "TestCube",
        "cuts": 2,
        "smooth": 0.0
    }):
        all_passed = False

    return all_passed

# =============================================================================
# TESTS POUR BATCH 3 : INSPECTION
# =============================================================================

def test_batch_3_inspection():
    """Test handlers for inspection tools"""
    print("\n" + "="*60)
    print("BATCH 3: INSPECTION HANDLERS")
    print("="*60)

    all_passed = True

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    # Test 1: get_mesh_stats
    print("\n--- Test 1: get_mesh_stats ---")
    if not test_handler("get_mesh_stats", {
        "object_name": "TestCube"
    }):
        all_passed = False

    # Test 2: get_object_bounds
    print("\n--- Test 2: get_object_bounds ---")
    if not test_handler("get_object_bounds", {
        "object_name": "TestCube",
        "world_space": True
    }):
        all_passed = False

    # Test 3: validate_mesh
    print("\n--- Test 3: validate_mesh ---")
    if not test_handler("validate_mesh", {
        "object_name": "TestCube",
        "fix_issues": False
    }):
        all_passed = False

    # Test 4: check_uvs
    print("\n--- Test 4: check_uvs ---")
    if not test_handler("check_uvs", {
        "object_name": "TestCube"
    }):
        all_passed = False

    return all_passed

# =============================================================================
# RUN ALL
# =============================================================================

def run_all_tests():
    """Run all batch tests"""
    print("\n" + "="*60)
    print("BRIDGE HANDLERS VALIDATION")
    print("="*60)

    if not COMMAND_HANDLERS:
        print("\n❌ COMMAND_HANDLERS not loaded! Cannot run tests.")
        print("Make sure the bridge addon is properly installed.")
        return False

    print(f"\nFound {len(COMMAND_HANDLERS)} handlers:")
    for handler_name in sorted(COMMAND_HANDLERS.keys()):
        print(f"  - {handler_name}")

    results = {}

    # Run batch tests
    results["BATCH 1"] = test_batch_1_mesh_editing()
    results["BATCH 2"] = test_batch_2_edge_operations()
    results["BATCH 3"] = test_batch_3_inspection()

    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    all_success = True
    for batch_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{batch_name}: {status}")
        if not passed:
            all_success = False

    print("\n" + "="*60)
    if all_success:
        print("✅✅✅ ALL HANDLERS VALIDATED")
        print("READY FOR MCP INTEGRATION")
    else:
        print("❌❌❌ SOME HANDLERS FAILED")
        print("FIX ISSUES BEFORE INTEGRATION")
    print("="*60)

    return all_success

# Auto-run when executed
if __name__ == "__main__":
    run_all_tests()
