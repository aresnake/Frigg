"""
Test saving viewport to image file directly

Alternative approach: save current viewport state to image file
"""

import bpy
import os
import base64

print("=" * 70)
print("TESTING IMAGE SAVE FROM VIEWPORT")
print("=" * 70)

try:
    width = 256
    height = 256

    print(f"\n[1/4] Creating new image buffer...")

    # Create a new image to hold the render
    image_name = "viewport_snapshot_temp"
    if image_name in bpy.data.images:
        bpy.data.images.remove(bpy.data.images[image_name])

    # Method 1: Try using image.save() after screen grab
    # Actually, let's try a simpler approach - save screenshot

    print(f"\n[2/4] Attempting screenshot save...")

    # Get temp directory
    import tempfile
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "frigg_viewport_test.png")

    print(f"      Temp path: {temp_path}")

    # Try to save screenshot
    # Note: This requires UI context
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                print(f"      Found VIEW_3D area")

                # Try setting up context and saving
                old_filepath = bpy.context.scene.render.filepath
                bpy.context.scene.render.filepath = temp_path

                # Try using screen.screenshot
                print(f"      Attempting bpy.ops.screen.screenshot...")

                try:
                    for region in area.regions:
                        if region.type == 'WINDOW':
                            with bpy.context.temp_override(window=window, area=area, region=region):
                                # This might work
                                bpy.ops.screen.screenshot(filepath=temp_path)
                            break
                    print(f"      Screenshot saved!")
                except Exception as screenshot_error:
                    print(f"      Screenshot failed: {screenshot_error}")

                bpy.context.scene.render.filepath = old_filepath
                break
        break

    print(f"\n[3/4] Checking if file exists...")

    if os.path.exists(temp_path):
        file_size = os.path.getsize(temp_path)
        print(f"      File exists: {file_size} bytes")

        # Read and encode
        print(f"\n[4/4] Encoding to base64...")
        with open(temp_path, 'rb') as f:
            image_data = f.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')

        print(f"      Base64 length: {len(base64_image)} chars")
        print(f"      First 60 chars: {base64_image[:60]}...")

        # Clean up
        os.remove(temp_path)

        print("\n" + "=" * 70)
        print("TEST PASSED!")
        print("=" * 70)

        result = "screenshot_works"
    else:
        print(f"      File NOT created at {temp_path}")
        print("\n" + "=" * 70)
        print("TEST FAILED - No file created")
        print("=" * 70)
        result = "no_file_created"

except Exception as e:
    print("\n" + "=" * 70)
    print("TEST FAILED!")
    print("=" * 70)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    result = f"error: {e}"

print("\nTest complete.")
