"""
Test script for execute_python meta-tool

This script will be executed inside Blender via the bridge.
"""

import bpy

# Count cubes in scene
cube_count = len([o for o in bpy.data.objects if 'Cube' in o.name])
print(f"Found {cube_count} cubes in the scene")

# Get scene info
scene = bpy.context.scene
print(f"Scene name: {scene.name}")
print(f"Frame range: {scene.frame_start} - {scene.frame_end}")
print(f"Total objects: {len(bpy.data.objects)}")

# Return result
result = {
    "cube_count": cube_count,
    "scene_name": scene.name,
    "total_objects": len(bpy.data.objects)
}
