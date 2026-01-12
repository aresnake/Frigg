"""
Test using Blender's render engine to capture viewport

This uses bpy.ops.render.render() which SHOULD work without UI context
"""

import bpy
import os
import base64
import tempfile

print("=" * 70)
print("TESTING CAMERA RENDER (Standard Blender Render)")
print("=" * 70)

try:
    width = 256
    height = 256

    print(f"\n[1/6] Setting up render settings...")

    scene = bpy.context.scene

    # Store original settings
    original_resolution_x = scene.render.resolution_x
    original_resolution_y = scene.render.resolution_y
    original_resolution_percentage = scene.render.resolution_percentage
    original_filepath = scene.render.filepath
    original_file_format = scene.render.image_settings.file_format

    # Set render settings
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    # Create temp file
    temp_path = os.path.join(tempfile.gettempdir(), "frigg_render_test.png")
    scene.render.filepath = temp_path

    print(f"      Resolution: {width}x{height}")
    print(f"      Output: {temp_path}")

    print(f"\n[2/6] Checking camera...")

    # Make sure we have a camera
    camera = scene.camera
    if not camera:
        print(f"      No camera, creating one...")
        bpy.ops.object.camera_add(location=(7.5, -6.5, 5.4))
        camera = bpy.context.active_object
        scene.camera = camera
    else:
        print(f"      Camera found: {camera.name}")

    print(f"\n[3/6] Setting render engine...")

    # Use Workbench for speed (like viewport solid mode)
    original_engine = scene.render.engine
    scene.render.engine = 'BLENDER_WORKBENCH'

    print(f"      Engine: {scene.render.engine}")

    print(f"\n[4/6] Rendering...")

    # This should work without UI context!
    bpy.ops.render.render(write_still=True)

    print(f"      Render complete!")

    print(f"\n[5/6] Reading image file...")

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

        print(f"\n[6/6] Restoring settings...")
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.resolution_percentage = original_resolution_percentage
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_file_format
        scene.render.engine = original_engine

        print("\n" + "=" * 70)
        print("TEST PASSED!")
        print("=" * 70)
        print("Standard render works! This can be used as fallback.")

        result = "camera_render_works"

    else:
        print(f"      File NOT created")
        print("\n" + "=" * 70)
        print("TEST FAILED")
        print("=" * 70)
        result = "no_file"

except Exception as e:
    print("\n" + "=" * 70)
    print("TEST FAILED!")
    print("=" * 70)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    result = f"error: {e}"

print("\nTest complete.")
