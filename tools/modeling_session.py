"""
Interactive modeling session to test Frigg tools and identify missing features.
"""

import json
import socket
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def bridge_call(method, params):
    """Send command to Blender bridge."""
    try:
        with socket.create_connection(("127.0.0.1", 8765), timeout=5) as sock:
            command = {"method": method, "params": params}
            sock.sendall((json.dumps(command) + "\n").encode())
            response = sock.makefile("r").readline()
            result = json.loads(response) if response else {"error": "No response"}

            if isinstance(result, dict) and result.get("ok"):
                return result["result"]
            elif isinstance(result, dict) and "error" in result:
                print(f"[ERROR] {result['error']}")
                return None
            return result
    except Exception as e:
        print(f"[ERROR] Bridge call failed: {e}")
        return None


def list_scene():
    """List all objects in the scene."""
    print("\n" + "="*60)
    print("SCENE OBJECTS")
    print("="*60)
    result = bridge_call("list_objects", {})
    if result and "objects" in result:
        for i, obj in enumerate(result["objects"], 1):
            print(f"{i}. {obj}")
    return result


def create_simple_table():
    """Create a simple table using basic primitives."""
    print("\n" + "="*60)
    print("MODELING: Simple Table")
    print("="*60)

    # Table top
    print("\n1. Creating table top...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "TableTop",
        "location": [0, 0, 1],
        "scale": [2, 1, 0.1]
    })

    # Table legs (4)
    print("2. Creating table legs...")
    leg_positions = [
        [-1.8, -0.8, 0.5],  # Front left
        [1.8, -0.8, 0.5],   # Front right
        [-1.8, 0.8, 0.5],   # Back left
        [1.8, 0.8, 0.5]     # Back right
    ]

    for i, pos in enumerate(leg_positions, 1):
        bridge_call("create_primitive", {
            "primitive_type": "cylinder",
            "name": f"TableLeg{i}",
            "location": pos,
            "scale": [0.1, 0.1, 0.5]
        })

    print("\n[OK] Table created!")
    list_scene()


def create_simple_crate():
    """Create a crate with beveled edges."""
    print("\n" + "="*60)
    print("MODELING: Simple Crate")
    print("="*60)

    # Base crate
    print("\n1. Creating base crate...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "Crate",
        "location": [3, 0, 0.5],
        "scale": 1
    })

    # Try to add bevel (will show if we need bevel tool)
    print("2. Attempting to add details...")
    print("[NOTE] Would need bevel_edges tool for rounded corners")

    # Add inset faces for detail
    print("3. Adding panel details with inset...")
    result = bridge_call("inset_faces", {
        "object_name": "Crate",
        "thickness": 0.05,
        "depth": -0.02
    })

    if result:
        print(f"[OK] Inset applied: {result['new_face_count']} faces")

    print("\n[OK] Crate created!")
    list_scene()


def create_simple_door():
    """Create a door with panels."""
    print("\n" + "="*60)
    print("MODELING: Door with Panels")
    print("="*60)

    # Door frame
    print("\n1. Creating door frame...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "DoorFrame",
        "location": [6, 0, 1],
        "scale": [1, 0.1, 2]
    })

    # Door panels (would need face selection and extrusion)
    print("2. Creating door panels...")
    print("[NOTE] Would benefit from:")
    print("   - Loop cut tool")
    print("   - Select face by index tool")
    print("   - Bevel modifier")

    # Try inset for panel effect
    result = bridge_call("inset_faces", {
        "object_name": "DoorFrame",
        "thickness": 0.1,
        "depth": 0.05
    })

    if result:
        print(f"[OK] Panel inset applied")

    print("\n[OK] Door created!")
    list_scene()


def create_detailed_box():
    """Create a box with handles using boolean operations."""
    print("\n" + "="*60)
    print("MODELING: Box with Boolean Cutouts")
    print("="*60)

    # Main box
    print("\n1. Creating main box...")
    bridge_call("create_primitive", {
        "primitive_type": "cube",
        "name": "DetailBox",
        "location": [9, 0, 0.5],
        "scale": [0.8, 0.6, 0.4]
    })

    # Create handle cutouts using boolean
    print("2. Creating handle cutouts...")
    bridge_call("create_primitive", {
        "primitive_type": "cylinder",
        "name": "HandleCut1",
        "location": [9, -0.7, 0.5],
        "rotation": [90, 0, 0],
        "scale": [0.1, 0.1, 0.3]
    })

    bridge_call("create_primitive", {
        "primitive_type": "cylinder",
        "name": "HandleCut2",
        "location": [9, 0.7, 0.5],
        "rotation": [90, 0, 0],
        "scale": [0.1, 0.1, 0.3]
    })

    # Apply boolean difference
    print("3. Applying boolean operations...")
    bridge_call("boolean_operation", {
        "base_object": "DetailBox",
        "target_object": "HandleCut1",
        "operation": "DIFFERENCE",
        "apply": False,
        "hide_target": True
    })

    bridge_call("boolean_operation", {
        "base_object": "DetailBox",
        "target_object": "HandleCut2",
        "operation": "DIFFERENCE",
        "apply": False,
        "hide_target": True
    })

    print("\n[OK] Detailed box created!")
    list_scene()


def test_join_workflow():
    """Test joining multiple objects."""
    print("\n" + "="*60)
    print("WORKFLOW TEST: Object Joining")
    print("="*60)

    # Create multiple small cubes
    print("\n1. Creating multiple components...")
    for i in range(3):
        bridge_call("create_primitive", {
            "primitive_type": "cube",
            "name": f"Component{i+1}",
            "location": [12 + i, 0, 0.5],
            "scale": 0.3
        })

    # Join them
    print("2. Joining components...")
    result = bridge_call("join_objects", {
        "object_names": ["Component1", "Component2", "Component3"],
        "result_name": "AssembledPart"
    })

    if result:
        print(f"[OK] Joined: {result['vertex_count']} vertices, {result['face_count']} faces")

    list_scene()


def identify_missing_tools():
    """Print a list of tools we discovered we need."""
    print("\n" + "="*60)
    print("MISSING TOOLS ANALYSIS")
    print("="*60)

    missing_tools = [
        {
            "name": "bevel_edges",
            "priority": "HIGH",
            "reason": "Essential for hard-surface modeling, rounding edges",
            "use_cases": ["Crates", "Furniture", "Props", "Mechanical parts"]
        },
        {
            "name": "subdivide_mesh",
            "priority": "HIGH",
            "reason": "Add geometry density for organic shapes",
            "use_cases": ["Organic models", "Smooth surfaces", "Terrain"]
        },
        {
            "name": "loop_cut",
            "priority": "MEDIUM",
            "reason": "Add edge loops for controlled topology",
            "use_cases": ["Character modeling", "Controlled deformation"]
        },
        {
            "name": "select_by_normal",
            "priority": "MEDIUM",
            "reason": "Select faces facing certain direction",
            "use_cases": ["Batch operations", "Automated workflows"]
        },
        {
            "name": "bridge_edge_loops",
            "priority": "MEDIUM",
            "reason": "Connect two edge loops",
            "use_cases": ["Holes", "Complex connections"]
        },
        {
            "name": "solidify_modifier",
            "priority": "LOW",
            "reason": "Already have via add_modifier, but could be dedicated",
            "use_cases": ["Shell objects", "Thickness"]
        },
        {
            "name": "apply_all_modifiers",
            "priority": "MEDIUM",
            "reason": "Apply all modifiers at once",
            "use_cases": ["Finalize models", "Batch operations"]
        },
        {
            "name": "recalculate_normals",
            "priority": "HIGH",
            "reason": "Fix inside-out faces",
            "use_cases": ["Every model cleanup"]
        },
        {
            "name": "triangulate",
            "priority": "LOW",
            "reason": "Convert to triangles for export",
            "use_cases": ["Game assets", "Export prep"]
        },
        {
            "name": "shade_smooth",
            "priority": "MEDIUM",
            "reason": "Set smooth shading",
            "use_cases": ["Visual quality", "Presentation"]
        }
    ]

    print("\nDiscovered needs during modeling session:\n")
    for tool in missing_tools:
        priority_color = {
            "HIGH": "***",
            "MEDIUM": "** ",
            "LOW": "*  "
        }
        marker = priority_color.get(tool["priority"], "")
        print(f"{marker} {tool['name']}")
        print(f"    Priority: {tool['priority']}")
        print(f"    Reason: {tool['reason']}")
        print(f"    Use cases: {', '.join(tool['use_cases'])}")
        print()

    return missing_tools


def main():
    """Run modeling tests."""
    print("\n" + "="*60)
    print("FRIGG MODELING SESSION")
    print("Interactive modeling to identify missing tools")
    print("="*60)

    # Check connection
    result = bridge_call("bridge_ping", {})
    if not result:
        print("[ERROR] Bridge not connected!")
        return False

    print("[OK] Bridge connected")

    # Show initial scene
    list_scene()

    # Run modeling tests
    create_simple_table()
    create_simple_crate()
    create_simple_door()
    create_detailed_box()
    test_join_workflow()

    # Analyze what we need
    missing_tools = identify_missing_tools()

    # Generate report
    print("\n" + "="*60)
    print("SESSION SUMMARY")
    print("="*60)
    print(f"\nTotal missing tools identified: {len(missing_tools)}")
    print(f"HIGH priority: {sum(1 for t in missing_tools if t['priority'] == 'HIGH')}")
    print(f"MEDIUM priority: {sum(1 for t in missing_tools if t['priority'] == 'MEDIUM')}")
    print(f"LOW priority: {sum(1 for t in missing_tools if t['priority'] == 'LOW')}")

    print("\n[OK] Modeling session complete!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
