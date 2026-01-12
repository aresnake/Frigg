"""
Test viewport_snapshot INLINE - runs directly in Blender via execute_python

This tests the function in the exact context where it will run,
without depending on external socket calls.
"""

import bpy
import base64
import tempfile
import os

print("=" * 70)
print("TESTING viewport_snapshot INLINE")
print("=" * 70)

# Test parameters
params = {
    'shading': 'solid',
    'projection': 'perspective',
    'view': 'current',
    'width': 256,
    'height': 256,
    'format': 'PNG'
}

print(f"\nTest params: {params}")
print("\nExecuting viewport_snapshot logic...")

try:
    # INLINE IMPLEMENTATION - exact copy of viewport_snapshot logic
    shading = params.get("shading", "solid")
    projection = params.get("projection", "perspective")
    view = params.get("view", "current")
    width = params.get("width", 512)
    height = params.get("height", 512)
    format_type = params.get("format", "PNG")

    target = params.get("target", None)
    isolate = params.get("isolate", False)
    fit_to_view = params.get("fit_to_view", False)
    show_overlays = params.get("show_overlays", True)

    # Step 1: Find 3D viewport
    print("\n[1/7] Finding 3D viewport...")
    area = None
    for window in bpy.context.window_manager.windows:
        for a in window.screen.areas:
            if a.type == 'VIEW_3D':
                area = a
                break
        if area:
            break

    if not area:
        raise RuntimeError("No 3D viewport found")
    print(f"      Found viewport area: {area.type}")

    space = area.spaces.active
    region_3d = space.region_3d

    # Step 2: Store original settings
    print("\n[2/7] Storing original settings...")
    original_shading = space.shading.type
    original_overlay = space.overlay.show_overlays
    original_view_perspective = region_3d.view_perspective
    print(f"      Original shading: {original_shading}")
    print(f"      Original view: {original_view_perspective}")

    # Step 3: Apply shading
    print("\n[3/7] Applying shading settings...")
    shading_map = {
        "solid": "SOLID",
        "wireframe": "WIREFRAME",
        "material": "MATERIAL",
        "rendered": "RENDERED"
    }
    space.shading.type = shading_map[shading]
    space.overlay.show_overlays = show_overlays
    print(f"      Set shading to: {space.shading.type}")

    # Step 4: Apply projection
    print("\n[4/7] Applying projection...")
    if projection == "ortho":
        region_3d.view_perspective = 'ORTHO'
    else:
        region_3d.view_perspective = 'PERSP'
    print(f"      Set projection to: {region_3d.view_perspective}")

    # Step 5: Setup render
    print("\n[5/7] Setting up render...")
    scene = bpy.context.scene
    original_resolution_x = scene.render.resolution_x
    original_resolution_y = scene.render.resolution_y
    original_filepath = scene.render.filepath

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_path = tmp.name

    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.filepath = temp_path
    print(f"      Resolution: {width}x{height}")
    print(f"      Temp file: {temp_path}")

    # Step 6: Render viewport
    print("\n[6/7] Rendering viewport...")

    # Find the correct context
    rendered = False
    for window in bpy.context.window_manager.windows:
        for a in window.screen.areas:
            if a.type == 'VIEW_3D':
                for region in a.regions:
                    if region.type == 'WINDOW':
                        print(f"      Found window region, attempting render...")
                        with bpy.context.temp_override(window=window, area=a, region=region):
                            bpy.ops.render.opengl(write_still=True)
                        rendered = True
                        break
                if rendered:
                    break
        if rendered:
            break

    if not rendered:
        raise RuntimeError("Could not render viewport - no WINDOW region found")

    print(f"      Render complete!")

    # Step 7: Read and encode image
    print("\n[7/7] Reading and encoding image...")

    if os.path.exists(temp_path):
        file_size = os.path.getsize(temp_path)
        print(f"      File exists: {file_size} bytes")

        with open(temp_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        print(f"      Base64 length: {len(base64_image)} chars")
        print(f"      First 60 chars: {base64_image[:60]}...")

        # Clean up
        os.remove(temp_path)
        print(f"      Cleaned up temp file")
    else:
        raise RuntimeError(f"Render file not created at {temp_path}")

    # Restore settings
    print("\n[CLEANUP] Restoring original settings...")
    space.shading.type = original_shading
    space.overlay.show_overlays = original_overlay
    region_3d.view_perspective = original_view_perspective
    scene.render.resolution_x = original_resolution_x
    scene.render.resolution_y = original_resolution_y
    scene.render.filepath = original_filepath
    print(f"      Restored!")

    # Return result
    result = {
        "success": True,
        "width": width,
        "height": height,
        "format": format_type,
        "image_length": len(base64_image),
        "image_preview": base64_image[:100]
    }

    print("\n" + "=" * 70)
    print("TEST PASSED!")
    print("=" * 70)
    print(f"Result: {result}")

except Exception as e:
    print("\n" + "=" * 70)
    print("TEST FAILED!")
    print("=" * 70)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    result = {"success": False, "error": str(e)}

print("\nTest complete.")
