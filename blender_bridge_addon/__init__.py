import bmesh
import bpy


def handle_join_objects(data):
    """Join multiple mesh objects."""
    try:
        object_names = data.get("object_names") or []
        result_name = data.get("result_name")

        if not isinstance(object_names, list) or len(object_names) < 2:
            return {"error": "Need at least 2 object names to join."}

        objects = []
        for name in object_names:
            if not name:
                return {"error": "Object name cannot be empty."}
            obj = bpy.data.objects.get(name)
            if not obj:
                return {"error": f"Object '{name}' not found."}
            if obj.type != "MESH":
                return {"error": f"Object '{name}' is not a mesh."}
            objects.append(obj)

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join()

        result_obj = bpy.context.view_layer.objects.active
        if not result_obj or result_obj.type != "MESH":
            return {"error": "Join operation failed to produce a mesh result."}

        if result_name:
            result_obj.name = result_name

        mesh = result_obj.data
        return {
            "result_object": result_obj.name,
            "vertex_count": len(mesh.vertices),
            "face_count": len(mesh.polygons),
            "merged_objects": object_names,
        }
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_extrude_faces(data):
    """Extrude faces on a mesh object."""
    try:
        object_name = data.get("object_name")
        face_indices = data.get("face_indices")
        offset = data.get("offset", 0.5)
        direction = data.get("direction")

        if not object_name:
            return {"error": "object_name is required."}
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object '{object_name}' not found."}
        if obj.type != "MESH":
            return {"error": f"Object '{object_name}' is not a mesh."}

        if direction is not None:
            if (
                not isinstance(direction, (list, tuple))
                or len(direction) != 3
                or not all(isinstance(v, (int, float)) for v in direction)
            ):
                return {"error": "direction must be [x, y, z] if provided."}

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if face_indices is None or face_indices == "all":
            for face in bm.faces:
                face.select = True
            selected_faces = [face.index for face in bm.faces]
        elif isinstance(face_indices, list):
            try:
                indices = {int(i) for i in face_indices}
            except (TypeError, ValueError):
                return {"error": "face_indices must be a list of integers."}
            selected_faces = []
            for face in bm.faces:
                face.select = face.index in indices
                if face.select:
                    selected_faces.append(face.index)
        else:
            return {"error": "face_indices must be a list of integers or 'all'."}

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        if not selected_faces:
            return {"error": "No faces selected for extrusion."}

        if direction is None:
            bpy.ops.mesh.extrude_region_shrink_fatten(value=float(offset))
        else:
            translation = [float(direction[i]) * float(offset) for i in range(3)]
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value": translation}
            )

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "extruded_faces": selected_faces,
            "new_vertex_count": len(obj.data.vertices),
        }
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_inset_faces(data):
    """Inset faces on a mesh object."""
    try:
        object_name = data.get("object_name")
        face_indices = data.get("face_indices")
        thickness = data.get("thickness", 0.1)
        depth = data.get("depth", 0.0)

        if not object_name:
            return {"error": "object_name is required."}
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object '{object_name}' not found."}
        if obj.type != "MESH":
            return {"error": f"Object '{object_name}' is not a mesh."}

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if face_indices is None:
            for face in bm.faces:
                face.select = True
            selected_faces = [face.index for face in bm.faces]
        elif isinstance(face_indices, list):
            try:
                indices = {int(i) for i in face_indices}
            except (TypeError, ValueError):
                return {"error": "face_indices must be a list of integers."}
            selected_faces = []
            for face in bm.faces:
                face.select = face.index in indices
                if face.select:
                    selected_faces.append(face.index)
        else:
            return {"error": "face_indices must be a list of integers."}

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        if not selected_faces:
            return {"error": "No faces selected for inset."}

        bpy.ops.mesh.inset(thickness=float(thickness), depth=float(depth))
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "inset_faces": selected_faces,
            "new_face_count": len(obj.data.polygons),
        }
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_merge_vertices(data):
    """Merge vertices by distance (remove doubles)."""
    try:
        object_name = data.get("object_name")
        distance = data.get("distance", 0.0001)

        if not object_name:
            return {"error": "object_name is required."}
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object '{object_name}' not found."}
        if obj.type != "MESH":
            return {"error": f"Object '{object_name}' is not a mesh."}
        if distance is None or float(distance) < 0:
            return {"error": "distance must be a non-negative number."}

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        vertices_before = len(bm.verts)

        bpy.ops.mesh.remove_doubles(threshold=float(distance))
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        bm = bmesh.from_edit_mesh(obj.data)
        vertices_after = len(bm.verts)

        return {
            "object": obj.name,
            "vertices_before": vertices_before,
            "vertices_after": vertices_after,
            "removed_count": max(0, vertices_before - vertices_after),
        }
    except Exception as exc:
        return {"error": str(exc)}
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_bevel_edges(params):
    """Bevel edges on a mesh object."""
    import bmesh

    try:
        object_name = params.get("object_name")
        edge_indices = params.get("edge_indices")
        width = params.get("width", 0.1)
        segments = params.get("segments", 2)
        profile = params.get("profile", 0.5)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()

        if edge_indices is None or edge_indices == "all":
            for edge in bm.edges:
                edge.select = True
            selected_edges = [edge.index for edge in bm.edges]
        elif isinstance(edge_indices, list):
            try:
                indices = {int(i) for i in edge_indices}
            except (TypeError, ValueError):
                raise ValueError("edge_indices must be a list of integers.")
            selected_edges = []
            for edge in bm.edges:
                edge.select = edge.index in indices
                if edge.select:
                    selected_edges.append(edge.index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        bpy.ops.mesh.bevel(offset=float(width), segments=int(segments), profile=float(profile))

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "beveled_edges": selected_edges,
            "new_vertex_count": len(obj.data.vertices),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_subdivide_mesh(params):
    """Subdivide mesh faces."""
    import bmesh

    try:
        object_name = params.get("object_name")
        cuts = params.get("cuts", 1)
        smooth = params.get("smooth", 0.0)
        face_indices = params.get("face_indices")

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        if face_indices is None:
            for face in bm.faces:
                face.select = True
            selected_faces = [face.index for face in bm.faces]
        elif isinstance(face_indices, list):
            try:
                indices = {int(i) for i in face_indices}
            except (TypeError, ValueError):
                raise ValueError("face_indices must be a list of integers.")
            selected_faces = []
            for face in bm.faces:
                face.select = face.index in indices
                if face.select:
                    selected_faces.append(face.index)

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        bpy.ops.mesh.subdivide(number_cuts=int(cuts), smoothness=float(smooth))

        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

        return {
            "object": obj.name,
            "subdivided_faces": selected_faces,
            "new_vertex_count": len(obj.data.vertices),
            "new_face_count": len(obj.data.polygons),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


def handle_recalculate_normals(params):
    """Recalculate face normals (fix inside-out faces)."""
    import bmesh

    try:
        object_name = params.get("object_name")
        inside = params.get("inside", False)

        if not object_name:
            raise ValueError("object_name is required.")
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object '{object_name}' not found.")
        if obj.type != "MESH":
            raise ValueError(f"Object '{object_name}' is not a mesh.")

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bpy.ops.mesh.normals_make_consistent(inside=bool(inside))

        return {
            "object": obj.name,
            "status": "recalculated",
            "face_count": len(obj.data.polygons),
        }
    finally:
        try:
            if bpy.context.object and bpy.context.object.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass


# ============================================================================
# COMMAND HANDLERS REGISTRY
# ============================================================================

COMMAND_HANDLERS = {
    "join_objects": handle_join_objects,
    "extrude_faces": handle_extrude_faces,
    "inset_faces": handle_inset_faces,
    "merge_vertices": handle_merge_vertices,
    "bevel_edges": handle_bevel_edges,
    "subdivide_mesh": handle_subdivide_mesh,
    "recalculate_normals": handle_recalculate_normals,
}
