"""
SPACE MARINE MODELING TOOLS - Prototypes for Testing
=====================================================

8 Essential tools for hard-surface modeling (Space Marine armor)
Test these via execute_python before integrating into MCP

Author: Claude + Adrien
Date: 2026-01-13
"""

import bpy
import math


# =============================================================================
# TOOL 1: ADD MODIFIER
# =============================================================================
def add_modifier(params):
    """
    Add a modifier to an object (Mirror, Subdivision, Boolean, Array, Solidify)

    Essential for Space Marine armor symmetry and detail.

    Parameters:
        object_name: str - Object to modify
        modifier_type: str - Type (MIRROR, SUBSURF, BOOLEAN, ARRAY, SOLIDIFY)
        name: str (optional) - Custom modifier name

        # Mirror specific
        axis_x: bool - Mirror on X axis (default: True)
        axis_y: bool - Mirror on Y axis (default: False)
        axis_z: bool - Mirror on Z axis (default: False)
        use_bisect_axis: [bool, bool, bool] - Bisect geometry on axes

        # Subdivision specific
        levels: int - Viewport subdivision levels (default: 2)
        render_levels: int - Render subdivision levels (default: 2)

        # Boolean specific
        operation: str - DIFFERENCE, UNION, INTERSECT
        target_object: str - Object to use for boolean

        # Array specific
        count: int - Number of copies (default: 2)
        offset_x: float - Offset on X axis (default: 2.0)
        offset_y: float - Offset on Y axis (default: 0.0)
        offset_z: float - Offset on Z axis (default: 0.0)

        # Solidify specific
        thickness: float - Thickness (default: 0.1)
        offset: float - Offset factor (default: 0.0)

    Returns:
        dict: Modifier info
    """
    object_name = params.get("object_name") or params.get("name")
    modifier_type = params.get("modifier_type") or params.get("type")
    custom_name = params.get("name") or params.get("modifier_name")

    if not object_name:
        raise ValueError("add_modifier requires 'object_name' parameter")
    if not modifier_type:
        raise ValueError("add_modifier requires 'modifier_type' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    # Create modifier
    mod_name = custom_name or f"{modifier_type.capitalize()}Modifier"
    modifier = obj.modifiers.new(name=mod_name, type=modifier_type)

    # Configure based on type
    if modifier_type == "MIRROR":
        modifier.use_axis[0] = params.get("axis_x", True)
        modifier.use_axis[1] = params.get("axis_y", False)
        modifier.use_axis[2] = params.get("axis_z", False)

        bisect = params.get("use_bisect_axis", [False, False, False])
        if len(bisect) >= 3:
            modifier.use_bisect_axis[0] = bisect[0]
            modifier.use_bisect_axis[1] = bisect[1]
            modifier.use_bisect_axis[2] = bisect[2]

    elif modifier_type == "SUBSURF":
        modifier.levels = params.get("levels", 2)
        modifier.render_levels = params.get("render_levels", 2)

    elif modifier_type == "BOOLEAN":
        operation = params.get("operation", "DIFFERENCE")
        modifier.operation = operation

        target_name = params.get("target_object")
        if target_name:
            target_obj = bpy.data.objects.get(target_name)
            if target_obj:
                modifier.object = target_obj

    elif modifier_type == "ARRAY":
        modifier.count = params.get("count", 2)
        modifier.relative_offset_displace[0] = params.get("offset_x", 2.0)
        modifier.relative_offset_displace[1] = params.get("offset_y", 0.0)
        modifier.relative_offset_displace[2] = params.get("offset_z", 0.0)

    elif modifier_type == "SOLIDIFY":
        modifier.thickness = params.get("thickness", 0.1)
        modifier.offset = params.get("offset", 0.0)

    return {
        "object": object_name,
        "modifier_name": modifier.name,
        "modifier_type": modifier_type,
        "status": "added"
    }


# =============================================================================
# TOOL 2: APPLY MODIFIER
# =============================================================================
def apply_modifier(params):
    """
    Apply (bake) a modifier to make it permanent

    Parameters:
        object_name: str - Object with modifier
        modifier_name: str - Name of modifier to apply

    Returns:
        dict: Operation status
    """
    object_name = params.get("object_name") or params.get("name")
    modifier_name = params.get("modifier_name")

    if not object_name:
        raise ValueError("apply_modifier requires 'object_name' parameter")
    if not modifier_name:
        raise ValueError("apply_modifier requires 'modifier_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    modifier = obj.modifiers.get(modifier_name)
    if not modifier:
        raise ValueError(f"Modifier '{modifier_name}' not found on '{object_name}'")

    # Apply modifier
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier_name)

    return {
        "object": object_name,
        "modifier": modifier_name,
        "status": "applied"
    }


# =============================================================================
# TOOL 3: LIST MODIFIERS
# =============================================================================
def list_modifiers(params):
    """
    List all modifiers on an object

    Parameters:
        object_name: str - Object to query

    Returns:
        dict: List of modifiers with details
    """
    object_name = params.get("object_name") or params.get("name")

    if not object_name:
        raise ValueError("list_modifiers requires 'object_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    modifiers = []
    for mod in obj.modifiers:
        mod_info = {
            "name": mod.name,
            "type": mod.type,
            "show_viewport": mod.show_viewport,
            "show_render": mod.show_render
        }

        # Add type-specific info
        if mod.type == "MIRROR":
            mod_info["axes"] = {
                "x": mod.use_axis[0],
                "y": mod.use_axis[1],
                "z": mod.use_axis[2]
            }
        elif mod.type == "SUBSURF":
            mod_info["levels"] = mod.levels
            mod_info["render_levels"] = mod.render_levels
        elif mod.type == "BOOLEAN":
            mod_info["operation"] = mod.operation
            mod_info["target"] = mod.object.name if mod.object else None

        modifiers.append(mod_info)

    return {
        "object": object_name,
        "modifier_count": len(modifiers),
        "modifiers": modifiers
    }


# =============================================================================
# TOOL 4: BOOLEAN OPERATION
# =============================================================================
def boolean_operation(params):
    """
    Perform boolean operation between two objects (Union/Difference/Intersect)

    Essential for Space Marine armor cuts and details.

    Parameters:
        base_object: str - Base object to modify
        target_object: str - Object to use for boolean
        operation: str - DIFFERENCE, UNION, INTERSECT (default: DIFFERENCE)
        apply: bool - Apply immediately (default: False)
        hide_target: bool - Hide target after operation (default: True)

    Returns:
        dict: Operation status
    """
    base_name = params.get("base_object") or params.get("object_name")
    target_name = params.get("target_object") or params.get("tool_object")
    operation = params.get("operation", "DIFFERENCE")
    apply_immediately = params.get("apply", False)
    hide_target = params.get("hide_target", True)

    if not base_name:
        raise ValueError("boolean_operation requires 'base_object' parameter")
    if not target_name:
        raise ValueError("boolean_operation requires 'target_object' parameter")

    base_obj = bpy.data.objects.get(base_name)
    target_obj = bpy.data.objects.get(target_name)

    if not base_obj:
        raise ValueError(f"Base object '{base_name}' not found")
    if not target_obj:
        raise ValueError(f"Target object '{target_name}' not found")

    # Add boolean modifier
    modifier = base_obj.modifiers.new(name=f"Boolean_{target_name}", type="BOOLEAN")
    modifier.operation = operation
    modifier.object = target_obj

    result = {
        "base_object": base_name,
        "target_object": target_name,
        "operation": operation,
        "modifier_name": modifier.name,
        "applied": False
    }

    # Apply if requested
    if apply_immediately:
        bpy.context.view_layer.objects.active = base_obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        result["applied"] = True

    # Hide target object
    if hide_target:
        target_obj.hide_set(True)
        result["target_hidden"] = True

    return result


# =============================================================================
# TOOL 5: CREATE MATERIAL
# =============================================================================
def create_material(params):
    """
    Create a new PBR material with Principled BSDF

    Parameters:
        name: str - Material name
        base_color: [r, g, b, a] - Base color (default: [0.8, 0.8, 0.8, 1.0])
        metallic: float - Metallic value 0-1 (default: 0.0)
        roughness: float - Roughness value 0-1 (default: 0.5)

    Returns:
        dict: Material info
    """
    mat_name = params.get("name") or params.get("material_name")
    if not mat_name:
        raise ValueError("create_material requires 'name' parameter")

    # Check if material exists
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)

    # Enable nodes
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    nodes.clear()

    # Create Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)

    # Create Material Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)

    # Link nodes
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Set properties
    base_color = params.get("base_color", [0.8, 0.8, 0.8, 1.0])
    if len(base_color) >= 4:
        bsdf.inputs['Base Color'].default_value = base_color

    metallic = params.get("metallic", 0.0)
    bsdf.inputs['Metallic'].default_value = metallic

    roughness = params.get("roughness", 0.5)
    bsdf.inputs['Roughness'].default_value = roughness

    return {
        "material_name": mat_name,
        "base_color": base_color,
        "metallic": metallic,
        "roughness": roughness,
        "status": "created"
    }


# =============================================================================
# TOOL 6: ASSIGN MATERIAL
# =============================================================================
def assign_material(params):
    """
    Assign a material to an object

    Parameters:
        object_name: str - Object to assign material to
        material_name: str - Material to assign
        slot_index: int (optional) - Material slot index (default: 0)

    Returns:
        dict: Assignment status
    """
    object_name = params.get("object_name") or params.get("name")
    material_name = params.get("material_name") or params.get("material")
    slot_index = params.get("slot_index", 0)

    if not object_name:
        raise ValueError("assign_material requires 'object_name' parameter")
    if not material_name:
        raise ValueError("assign_material requires 'material_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    mat = bpy.data.materials.get(material_name)
    if not mat:
        raise ValueError(f"Material '{material_name}' not found")

    # Ensure object has material slots
    if len(obj.data.materials) == 0:
        obj.data.materials.append(mat)
    else:
        if slot_index >= len(obj.data.materials):
            obj.data.materials.append(mat)
        else:
            obj.data.materials[slot_index] = mat

    return {
        "object": object_name,
        "material": material_name,
        "slot": slot_index,
        "status": "assigned"
    }


# =============================================================================
# TOOL 7: CREATE COLLECTION
# =============================================================================
def create_collection(params):
    """
    Create a new collection for organizing objects

    Parameters:
        name: str - Collection name
        parent_collection: str (optional) - Parent collection name

    Returns:
        dict: Collection info
    """
    collection_name = params.get("name") or params.get("collection_name")
    parent_name = params.get("parent_collection")

    if not collection_name:
        raise ValueError("create_collection requires 'name' parameter")

    # Check if collection exists
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
        status = "exists"
    else:
        collection = bpy.data.collections.new(collection_name)
        status = "created"

        # Link to parent or scene
        if parent_name:
            parent = bpy.data.collections.get(parent_name)
            if parent:
                parent.children.link(collection)
            else:
                raise ValueError(f"Parent collection '{parent_name}' not found")
        else:
            bpy.context.scene.collection.children.link(collection)

    return {
        "collection_name": collection_name,
        "parent": parent_name,
        "status": status
    }


# =============================================================================
# TOOL 8: MOVE TO COLLECTION
# =============================================================================
def move_to_collection(params):
    """
    Move an object to a collection

    Parameters:
        object_name: str - Object to move
        collection_name: str - Target collection
        unlink_from_current: bool - Unlink from current collections (default: True)

    Returns:
        dict: Move status
    """
    object_name = params.get("object_name") or params.get("name")
    collection_name = params.get("collection_name") or params.get("collection")
    unlink_current = params.get("unlink_from_current", True)

    if not object_name:
        raise ValueError("move_to_collection requires 'object_name' parameter")
    if not collection_name:
        raise ValueError("move_to_collection requires 'collection_name' parameter")

    obj = bpy.data.objects.get(object_name)
    if not obj:
        raise ValueError(f"Object '{object_name}' not found")

    collection = bpy.data.collections.get(collection_name)
    if not collection:
        raise ValueError(f"Collection '{collection_name}' not found")

    # Unlink from current collections
    old_collections = []
    if unlink_current:
        for col in obj.users_collection:
            col.objects.unlink(obj)
            old_collections.append(col.name)

    # Link to new collection
    collection.objects.link(obj)

    return {
        "object": object_name,
        "new_collection": collection_name,
        "unlinked_from": old_collections if unlink_current else [],
        "status": "moved"
    }


# =============================================================================
# UTILITY: Test all tools
# =============================================================================
def test_all_space_marine_tools():
    """
    Complete test sequence for Space Marine modeling workflow

    This creates a simple armor piece with:
    - Symmetric modeling (Mirror)
    - Smooth subdivision
    - Boolean cuts
    - Blue metallic material
    - Organized in collection
    """
    print("\n" + "="*60)
    print("SPACE MARINE TOOLS - Complete Test")
    print("="*60 + "\n")

    try:
        # Clean scene
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # 1. Create base armor piece
        print("[1/8] Creating base cube...")
        bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), scale=(2, 1, 0.5))
        base = bpy.context.active_object
        base.name = "ArmorPlate"

        # 2. Add Mirror modifier
        print("[2/8] Adding Mirror modifier...")
        result = add_modifier({
            "object_name": "ArmorPlate",
            "modifier_type": "MIRROR",
            "axis_x": True,
            "use_bisect_axis": [True, False, False]
        })
        print(f"     → {result}")

        # 3. Add Subdivision modifier
        print("[3/8] Adding Subdivision modifier...")
        result = add_modifier({
            "object_name": "ArmorPlate",
            "modifier_type": "SUBSURF",
            "levels": 2
        })
        print(f"     → {result}")

        # 4. Create boolean cutter
        print("[4/8] Creating boolean cutter...")
        bpy.ops.mesh.primitive_cylinder_add(
            location=(0.5, 0, 0),
            rotation=(0, math.radians(90), 0),
            scale=(0.2, 0.2, 1.5)
        )
        cutter = bpy.context.active_object
        cutter.name = "BoltHole"

        # 5. Perform boolean operation
        print("[5/8] Performing boolean difference...")
        result = boolean_operation({
            "base_object": "ArmorPlate",
            "target_object": "BoltHole",
            "operation": "DIFFERENCE",
            "apply": False,
            "hide_target": True
        })
        print(f"     → {result}")

        # 6. Create Ultramarine Blue material
        print("[6/8] Creating Ultramarine Blue material...")
        result = create_material({
            "name": "UltramarineBlue",
            "base_color": [0.1, 0.3, 0.9, 1.0],
            "metallic": 0.9,
            "roughness": 0.3
        })
        print(f"     → {result}")

        # 7. Assign material
        print("[7/8] Assigning material...")
        result = assign_material({
            "object_name": "ArmorPlate",
            "material_name": "UltramarineBlue"
        })
        print(f"     → {result}")

        # 8. Organize in collection
        print("[8/8] Creating collection and organizing...")
        create_collection({"name": "SpaceMarine_Armor"})
        result = move_to_collection({
            "object_name": "ArmorPlate",
            "collection_name": "SpaceMarine_Armor"
        })
        print(f"     → {result}")

        # List final modifiers
        print("\n[FINAL] Listing modifiers on ArmorPlate...")
        modifiers = list_modifiers({"object_name": "ArmorPlate"})
        print(f"     → {modifiers['modifier_count']} modifiers:")
        for mod in modifiers['modifiers']:
            print(f"        - {mod['name']} ({mod['type']})")

        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED - Space Marine tools ready!")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    # Run test when executed via execute_python
    test_all_space_marine_tools()
