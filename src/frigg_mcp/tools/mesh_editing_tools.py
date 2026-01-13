from typing import Any, Dict, List, Optional, Union

from mcp.server import Server

from ..bridge import send_blender_command

mcp = Server("frigg")


@mcp.tool()
async def frigg_blender_join_objects(
    object_names: List[str],
    result_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Merge multiple mesh objects into one.

    Args:
        object_names: List of mesh object names to join.
        result_name: Optional name for the resulting object.

    Returns:
        Dict with result_object, vertex_count, face_count, merged_objects.
    """
    cmd = {
        "action": "join_objects",
        "object_names": object_names,
        "result_name": result_name,
    }
    result = await send_blender_command(cmd)
    if isinstance(result, dict) and "error" in result:
        return {"error": result["error"]}
    return result


@mcp.tool()
async def frigg_blender_extrude_faces(
    object_name: str,
    face_indices: Union[List[int], str],
    offset: float = 0.5,
    direction: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    Extrude selected faces on a mesh object.

    Args:
        object_name: Mesh object name to edit.
        face_indices: List of face indices to extrude or "all".
        offset: Extrusion distance (default: 0.5).
        direction: Optional direction [x, y, z]. None uses face normals.

    Returns:
        Dict with object, extruded_faces, new_vertex_count.
    """
    cmd = {
        "action": "extrude_faces",
        "object_name": object_name,
        "face_indices": face_indices,
        "offset": offset,
        "direction": direction,
    }
    result = await send_blender_command(cmd)
    if isinstance(result, dict) and "error" in result:
        return {"error": result["error"]}
    return result


@mcp.tool()
async def frigg_blender_inset_faces(
    object_name: str,
    face_indices: Optional[List[int]] = None,
    thickness: float = 0.1,
    depth: float = 0.0,
) -> Dict[str, Any]:
    """
    Create insets on selected faces.

    Args:
        object_name: Mesh object name to edit.
        face_indices: Optional list of face indices (None = all faces).
        thickness: Inset thickness (default: 0.1).
        depth: Inset depth (default: 0.0).

    Returns:
        Dict with object, inset_faces, new_face_count.
    """
    cmd = {
        "action": "inset_faces",
        "object_name": object_name,
        "face_indices": face_indices,
        "thickness": thickness,
        "depth": depth,
    }
    result = await send_blender_command(cmd)
    if isinstance(result, dict) and "error" in result:
        return {"error": result["error"]}
    return result


@mcp.tool()
async def frigg_blender_merge_vertices(
    object_name: str,
    distance: float = 0.0001,
) -> Dict[str, Any]:
    """
    Merge vertices by distance (remove doubles).

    Args:
        object_name: Mesh object name to edit.
        distance: Merge distance threshold (default: 0.0001).

    Returns:
        Dict with object, vertices_before, vertices_after, removed_count.
    """
    cmd = {
        "action": "merge_vertices",
        "object_name": object_name,
        "distance": distance,
    }
    result = await send_blender_command(cmd)
    if isinstance(result, dict) and "error" in result:
        return {"error": result["error"]}
    return result
