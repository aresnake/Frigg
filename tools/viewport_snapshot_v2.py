"""
viewport_snapshot v2 - Working version using camera render

Replace the old viewport_snapshot function in frigg_blender_bridge.py with this version.
"""

def viewport_snapshot(params):
    """
    VISION TOOL: Capture viewport snapshot using camera render

    Uses standard Blender rendering (WORKBENCH engine) instead of viewport opengl
    because the bridge runs without UI context.
    """
    import base64
    import tempfile
    import bpy
    import os
    import mathutils

    # Parameters with defaults
    shading = params.get("shading", "solid")  # solid | wireframe | material | rendered
    projection = params.get("projection", "perspective")  # perspective | ortho
    view = params.get("view", "current")  # current | camera | front | back | left | right | top | bottom
    width = params.get("width", 512)
    height = params.get("height", 512)
    format_type = params.get("format", "PNG")  # PNG | JPEG

    # Optional parameters
    target = params.get("target", None)
    isolate = params.get("isolate", False)
    fit_to_view = params.get("fit_to_view", False)

    # Validate parameters
    valid_shadings = ["solid", "wireframe", "material", "rendered"]
    if shading not in valid_shadings:
        raise ValueError(f"shading must be one of {valid_shadings}, got '{shading}'")

    valid_projections = ["perspective", "ortho"]
    if projection not in valid_projections:
        raise ValueError(f"projection must be one of {valid_projections}, got '{projection}'")

    valid_views = ["current", "camera", "front", "back", "left", "right", "top", "bottom"]
    if view not in valid_views:
        raise ValueError(f"view must be one of {valid_views}, got '{view}'")

    scene = bpy.context.scene

    # Store original settings
    original_resolution_x = scene.render.resolution_x
    original_resolution_y = scene.render.resolution_y
    original_resolution_percentage = scene.render.resolution_percentage
    original_filepath = scene.render.filepath
    original_file_format = scene.render.image_settings.file_format
    original_engine = scene.render.engine

    # Store original camera (if exists)
    original_camera = scene.camera
    temp_camera_created = False

    # Store visibility if isolating
    original_visibility = {}
    if isolate and target:
        for obj in bpy.data.objects:
            original_visibility[obj.name] = obj.hide_render

    try:
        # Create/setup camera for snapshot
        if view == "camera" and original_camera:
            # Use existing camera
            camera = original_camera
        else:
            # Create temporary camera manually (no bpy.ops - no UI context needed!)
            camera_data = bpy.data.cameras.new(name="_frigg_temp_camera_data")
            camera = bpy.data.objects.new("_frigg_temp_camera", camera_data)
            scene.collection.objects.link(camera)
            scene.camera = camera
            temp_camera_created = True

            # Position camera based on view
            if view == "current":
                # Try to get current viewport view
                for window in bpy.context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            space = area.spaces.active
                            region_3d = space.region_3d

                            # Copy viewport camera position
                            camera.location = region_3d.view_location.copy()
                            camera.rotation_euler = region_3d.view_rotation.to_euler()

                            # Adjust distance
                            view_dir = region_3d.view_rotation @ mathutils.Vector((0, 0, -1))
                            camera.location -= view_dir * region_3d.view_distance
                            break
                    break
            else:
                # Standard orthographic views
                view_configs = {
                    "front": ((0, -10, 0), (90, 0, 0)),
                    "back": ((0, 10, 0), (90, 0, 180)),
                    "right": ((10, 0, 0), (90, 0, 90)),
                    "left": ((-10, 0, 0), (90, 0, -90)),
                    "top": ((0, 0, 10), (0, 0, 0)),
                    "bottom": ((0, 0, -10), (180, 0, 0))
                }

                if view in view_configs:
                    loc, rot = view_configs[view]
                    camera.location = loc
                    camera.rotation_euler = [r * 3.14159 / 180 for r in rot]

        # Set camera projection
        if projection == "ortho":
            camera.data.type = 'ORTHO'
            camera.data.ortho_scale = 10.0  # Default ortho scale
        else:
            camera.data.type = 'PERSP'

        # Handle target isolation and framing
        if target:
            target_obj = bpy.data.objects.get(target)
            if not target_obj:
                raise ValueError(f"Target object '{target}' not found")

            if isolate:
                # Hide all objects except target in render
                for obj in bpy.data.objects:
                    obj.hide_render = (obj.name != target)

            if fit_to_view:
                # Point camera at target
                direction = target_obj.location - camera.location
                rot_quat = direction.to_track_quat('-Z', 'Y')
                camera.rotation_euler = rot_quat.to_euler()

        # Setup render settings
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = format_type

        # Set render engine based on shading
        if shading == "rendered":
            # Keep original engine (EEVEE/CYCLES)
            pass
        elif shading == "material":
            scene.render.engine = 'BLENDER_EEVEE'
        else:
            # Use WORKBENCH for solid/wireframe (fastest)
            scene.render.engine = 'BLENDER_WORKBENCH'

            # Configure workbench shading
            if shading == "wireframe":
                scene.display.shading.type = 'WIREFRAME'
            else:  # solid
                scene.display.shading.type = 'SOLID'

        # Create temp file path
        with tempfile.NamedTemporaryFile(suffix=f".{format_type.lower()}", delete=False) as tmp:
            temp_path = tmp.name

        scene.render.filepath = temp_path

        # Render!
        bpy.ops.render.render(write_still=True)

        # Read image and encode to base64
        if os.path.exists(temp_path):
            with open(temp_path, 'rb') as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

            # Clean up temp file
            os.remove(temp_path)
        else:
            raise RuntimeError(f"Render file not created at {temp_path}")

        # Prepare result
        view_info = {
            "shading": shading,
            "projection": projection,
            "view": view,
            "camera_location": list(camera.location),
            "camera_rotation": list(camera.rotation_euler),
            "render_engine": scene.render.engine
        }

        return {
            "success": True,
            "image": base64_image,
            "format": format_type,
            "width": width,
            "height": height,
            "view_info": view_info
        }

    finally:
        # Restore settings
        scene.render.resolution_x = original_resolution_x
        scene.render.resolution_y = original_resolution_y
        scene.render.resolution_percentage = original_resolution_percentage
        scene.render.filepath = original_filepath
        scene.render.image_settings.file_format = original_file_format
        scene.render.engine = original_engine
        scene.camera = original_camera

        # Delete temporary camera
        if temp_camera_created and camera:
            bpy.data.objects.remove(camera, do_unlink=True)

        # Restore visibility
        if isolate and target:
            for obj_name, was_hidden in original_visibility.items():
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.hide_render = was_hidden
