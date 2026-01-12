#!/usr/bin/env python3
"""
Frigg MCP - Tool Prototyping & Testing

This script allows rapid prototyping and testing of new Blender tools
before official integration into the MCP server.

Usage:
    python tools/prototype_tools.py <tool_name> [args...]

Examples:
    python tools/prototype_tools.py get_viewport_screenshot
    python tools/prototype_tools.py measure_distance Cube Camera
    python tools/prototype_tools.py test_all
"""

import json
import socket
import sys
import base64
from pathlib import Path
from typing import Any, Dict, Optional


def call_bridge(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Call the Blender bridge"""
    # Read bridge config
    state_file = Path(__file__).parent.parent / ".frigg_bridge.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
            host = state.get("host", "127.0.0.1")
            port = state.get("port", 8765)
    else:
        host = "127.0.0.1"
        port = 8765

    # Send request
    request = {"method": method, "params": params}
    data = json.dumps(request) + "\n"

    try:
        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall(data.encode("utf-8"))
            file = sock.makefile("r", encoding="utf-8")
            line = file.readline()
            if not line:
                return {"error": "Empty response from bridge"}
            response = json.loads(line)
        return response
    except ConnectionRefusedError:
        return {"error": f"Cannot connect to bridge at {host}:{port}. Start it first with: .\\tools\\frigg-bridge.ps1 -UI"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# PROTOTYPE TOOLS - Test here before adding to official MCP
# ============================================================================

def prototype_get_viewport_screenshot(width=512, height=512, angle="perspective"):
    """
    Capture viewport as screenshot

    This will be tool: frigg.blender.get_viewport_screenshot
    """
    print(f" Capturing viewport screenshot ({width}x{height}, {angle} view)...")

    result = call_bridge("get_viewport_screenshot", {
        "width": width,
        "height": height,
        "angle": angle
    })

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    # Save image to file
    if "result" in result and "image_base64" in result["result"]:
        image_data = base64.b64decode(result["result"]["image_base64"])
        output_path = Path("logs") / f"viewport_{angle}.png"
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f" Screenshot saved to: {output_path}")
        print(f"   Size: {len(image_data)} bytes")
        print(f"   Dimensions: {result['result']['width']}x{result['result']['height']}")
        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_measure_distance(obj1: str, obj2: str):
    """
    Measure distance between two objects

    This will be tool: frigg.blender.measure_distance
    """
    print(f" Measuring distance between '{obj1}' and '{obj2}'...")

    result = call_bridge("measure_distance", {
        "object1": obj1,
        "object2": obj2
    })

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result:
        distance = result["result"].get("distance", 0)
        print(f" Distance: {distance:.4f} Blender units")

        if "world_distance" in result["result"]:
            world_dist = result["result"]["world_distance"]
            print(f"   Real-world: {world_dist['meters']:.2f}m = {world_dist['centimeters']:.1f}cm")

        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_get_spatial_relationships(obj_name: str):
    """
    Get spatial relationships for an object

    This will be tool: frigg.blender.get_spatial_relationships
    """
    print(f" Getting spatial relationships for '{obj_name}'...")

    result = call_bridge("get_spatial_relationships", {
        "object_name": obj_name
    })

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result:
        data = result["result"]
        print(f" Object: {data.get('name')}")
        print(f"   Position: {data.get('location')}")
        print(f"   Bounding box size: {data.get('dimensions')}")

        if "nearest_objects" in data:
            print(f"   Nearest objects:")
            for obj in data["nearest_objects"][:5]:
                print(f"     - {obj['name']}: {obj['distance']:.2f} units ({obj['direction']})")

        if "in_camera_view" in data:
            print(f"   In camera view: {data['in_camera_view']}")

        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_check_intersection(obj1: str, obj2: str):
    """
    Check if two objects intersect

    This will be tool: frigg.blender.check_intersection
    """
    print(f" Checking intersection between '{obj1}' and '{obj2}'...")

    result = call_bridge("check_intersection", {
        "object1": obj1,
        "object2": obj2
    })

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result:
        data = result["result"]
        intersecting = data.get("intersecting", False)

        if intersecting:
            print(f"  Objects ARE intersecting!")
            if "overlap_volume" in data:
                print(f"   Overlap volume: {data['overlap_volume']:.6f}")
        else:
            print(f" Objects are NOT intersecting")
            if "min_distance" in data:
                print(f"   Minimum distance: {data['min_distance']:.4f}")

        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_render_preview(samples=32, width=512, height=512):
    """
    Render quick preview

    This will be tool: frigg.blender.render_preview
    """
    print(f" Rendering preview ({width}x{height}, {samples} samples)...")

    result = call_bridge("render_preview", {
        "samples": samples,
        "width": width,
        "height": height
    })

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result and "image_base64" in result["result"]:
        image_data = base64.b64decode(result["result"]["image_base64"])
        output_path = Path("logs") / "render_preview.png"
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f" Render saved to: {output_path}")
        print(f"   Size: {len(image_data)} bytes")
        print(f"   Render time: {result['result'].get('render_time', 'N/A')}s")
        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_get_scene_graph():
    """
    Get hierarchical scene structure

    This will be tool: frigg.blender.get_scene_graph
    """
    print(f" Getting scene graph...")

    result = call_bridge("get_scene_graph", {})

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result:
        def print_tree(obj, indent=0):
            prefix = "  " * indent + (" " if indent > 0 else "")
            print(f"{prefix}{obj['name']} ({obj['type']})")
            for child in obj.get("children", []):
                print_tree(child, indent + 1)

        data = result["result"]
        print(f" Scene: {data.get('scene_name')}")
        print(f"   Total objects: {data.get('total_objects')}")
        print(f"   Object tree:")
        for obj in data.get("objects", []):
            print_tree(obj, indent=1)

        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_viewport_snapshot(shading="solid", projection="perspective", view="current", width=512, height=512):
    """
    Capture viewport snapshot using camera render

    The VISION tool - allows Claude to see the scene!
    """
    print(f" Capturing viewport snapshot...")
    print(f"   Shading: {shading}")
    print(f"   Projection: {projection}")
    print(f"   View: {view}")
    print(f"   Resolution: {width}x{height}")

    result = call_bridge("viewport_snapshot", {
        "shading": shading,
        "projection": projection,
        "view": view,
        "width": width,
        "height": height
    })

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result:
        data = result["result"]

        if data.get("success"):
            print(f" Success!")
            print(f"   Format: {data['format']}")
            print(f"   Image data: {len(data['image'])} chars (base64)")
            print(f"   View info: {data['view_info']['view']} / {data['view_info']['shading']}")
            print(f"   Render engine: {data['view_info']['render_engine']}")

            # Save to file for inspection
            import base64
            import tempfile
            import os

            temp_path = os.path.join(tempfile.gettempdir(), f"frigg_snapshot_{shading}_{view}.png")
            with open(temp_path, 'wb') as f:
                f.write(base64.b64decode(data['image']))

            print(f"   Saved to: {temp_path}")
        else:
            print(f" Failed: {data}")

        return result
    else:
        print(f" Unexpected response: {result}")
        return result


def prototype_execute_python(script: str):
    """
    Execute arbitrary Python code in Blender

    This is a META-TOOL for rapid prototyping.
    Allows testing new tool ideas without restarting the bridge.
    """
    print(f" Executing Python script in Blender...")
    print(f"   Script length: {len(script)} characters")

    result = call_bridge("execute_python", {"script": script})

    if "error" in result:
        print(f" Error: {result['error']}")
        return result

    if "result" in result:
        data = result["result"]

        if data.get("success"):
            print(f" Script executed successfully!")

            if data.get("stdout"):
                print(f"   stdout:")
                for line in data["stdout"].strip().split("\n"):
                    print(f"     {line}")

            if data.get("stderr"):
                print(f"   stderr:")
                for line in data["stderr"].strip().split("\n"):
                    print(f"     {line}")

            if data.get("result") is not None:
                print(f"   result: {data['result']}")
        else:
            print(f" Script failed!")
            print(f"   Error: {data.get('error')}")
            print(f"   Type: {data.get('error_type')}")
            if data.get("traceback"):
                print(f"   Traceback:")
                for line in data["traceback"].strip().split("\n"):
                    print(f"     {line}")

        return result
    else:
        print(f" Unexpected response: {result}")
        return result


# ============================================================================
# TEST SUITE
# ============================================================================

def test_all():
    """Run all prototype tests"""
    print("=" * 70)
    print("FRIGG MCP - PROTOTYPE TOOL TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        ("Scene Graph", lambda: prototype_get_scene_graph()),
        ("Viewport Screenshot", lambda: prototype_get_viewport_screenshot(256, 256, "perspective")),
        ("Measure Distance (Cube-Camera)", lambda: prototype_measure_distance("Cube", "Camera")),
        ("Spatial Relationships (Cube)", lambda: prototype_get_spatial_relationships("Cube")),
        ("Intersection Check (Cube-Light)", lambda: prototype_check_intersection("Cube", "Light")),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print()
        print("-" * 70)
        print(f"TEST: {name}")
        print("-" * 70)
        try:
            result = test_func()
            if result and "error" not in result:
                passed += 1
                print(f" PASSED")
            else:
                failed += 1
                print(f" FAILED")
        except Exception as e:
            failed += 1
            print(f" EXCEPTION: {e}")
        print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nAvailable prototype tools:")
        print("  - viewport_snapshot [shading] [projection] [view] [width] [height]")
        print("  - get_viewport_screenshot [width] [height] [angle]")
        print("  - measure_distance <obj1> <obj2>")
        print("  - get_spatial_relationships <object>")
        print("  - check_intersection <obj1> <obj2>")
        print("  - render_preview [samples] [width] [height]")
        print("  - get_scene_graph")
        print("  - execute_python <script_file>")
        print("  - test_all")
        sys.exit(1)

    tool = sys.argv[1]
    args = sys.argv[2:]

    if tool == "test_all":
        test_all()

    elif tool == "viewport_snapshot":
        shading = args[0] if len(args) > 0 else "solid"
        projection = args[1] if len(args) > 1 else "perspective"
        view = args[2] if len(args) > 2 else "current"
        width = int(args[3]) if len(args) > 3 else 512
        height = int(args[4]) if len(args) > 4 else 512
        prototype_viewport_snapshot(shading, projection, view, width, height)

    elif tool == "get_viewport_screenshot":
        width = int(args[0]) if len(args) > 0 else 512
        height = int(args[1]) if len(args) > 1 else 512
        angle = args[2] if len(args) > 2 else "perspective"
        prototype_get_viewport_screenshot(width, height, angle)

    elif tool == "measure_distance":
        if len(args) < 2:
            print("Error: Need two object names")
            sys.exit(1)
        prototype_measure_distance(args[0], args[1])

    elif tool == "get_spatial_relationships":
        if len(args) < 1:
            print("Error: Need object name")
            sys.exit(1)
        prototype_get_spatial_relationships(args[0])

    elif tool == "check_intersection":
        if len(args) < 2:
            print("Error: Need two object names")
            sys.exit(1)
        prototype_check_intersection(args[0], args[1])

    elif tool == "render_preview":
        samples = int(args[0]) if len(args) > 0 else 32
        width = int(args[1]) if len(args) > 1 else 512
        height = int(args[2]) if len(args) > 2 else 512
        prototype_render_preview(samples, width, height)

    elif tool == "get_scene_graph":
        prototype_get_scene_graph()

    elif tool == "execute_python":
        if len(args) < 1:
            print("Error: Need script file path or inline script")
            print("\nExamples:")
            print("  python tools/prototype_tools.py execute_python test_script.py")
            print("  python tools/prototype_tools.py execute_python \"print('Hello from Blender')\"")
            sys.exit(1)

        script_arg = args[0]
        # Check if it's a file path
        if Path(script_arg).exists():
            with open(script_arg, 'r') as f:
                script = f.read()
            print(f"Loading script from: {script_arg}")
        else:
            # Treat as inline script
            script = script_arg

        prototype_execute_python(script)

    else:
        print(f"Unknown tool: {tool}")
        print("Run without arguments to see available tools")
        sys.exit(1)


if __name__ == "__main__":
    main()
