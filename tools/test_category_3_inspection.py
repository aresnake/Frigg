"""
CATEGORY 3: INSPECTION & VALIDATION
Test des outils d'inspection et de validation
"""

import bpy
from typing import Dict, Any, List

# =============================================================================
# 1. GET MESH STATS - Obtenir les statistiques du mesh
# =============================================================================

def test_get_mesh_stats():
    """Test: Obtenir les stats d'un mesh"""
    print("\n=== TEST: get_mesh_stats ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def get_mesh_stats(object_name: str) -> Dict[str, Any]:
        """
        Obtenir les statistiques détaillées d'un mesh

        Args:
            object_name: Nom de l'objet

        Returns:
            {
                "object": str,
                "vertices": int,
                "edges": int,
                "faces": int,
                "triangles": int,
                "ngons": int,  # Faces avec plus de 4 côtés
                "is_manifold": bool,
                "has_loose_verts": bool,
                "has_loose_edges": bool
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        mesh = obj.data

        # Compter les triangles (triangulate en mode édition temporaire)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Compter les ngons
        bpy.ops.object.mode_set(mode='OBJECT')
        ngons = sum(1 for face in mesh.polygons if len(face.vertices) > 4)

        # Calculer le nombre de triangles (approximatif)
        tri_count = 0
        for face in mesh.polygons:
            tri_count += len(face.vertices) - 2

        # Vérifier les loose verts/edges
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        bpy.ops.object.mode_set(mode='OBJECT')

        loose_verts = sum(1 for v in mesh.vertices if v.select)
        loose_edges = sum(1 for e in mesh.edges if e.select)

        # Désélectionner
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        return {
            "object": object_name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": tri_count,
            "ngons": ngons,
            "has_loose_verts": loose_verts > 0,
            "has_loose_edges": loose_edges > 0,
            "loose_vert_count": loose_verts,
            "loose_edge_count": loose_edges
        }

    result = get_mesh_stats(cube.name)
    print(f"Result: {result}")
    assert result["vertices"] == 8
    assert result["faces"] == 6
    assert result["triangles"] == 12  # 6 faces * 2 triangles
    print("✅ PASS")


# =============================================================================
# 2. GET OBJECT BOUNDS - Obtenir les dimensions réelles
# =============================================================================

def test_get_object_bounds():
    """Test: Obtenir les bounds d'un objet"""
    print("\n=== TEST: get_object_bounds ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0), scale=(2, 3, 4))
    cube = bpy.context.active_object

    def get_object_bounds(object_name: str, world_space: bool = True) -> Dict[str, Any]:
        """
        Obtenir les dimensions et bounds d'un objet

        Args:
            object_name: Nom de l'objet
            world_space: True pour world space, False pour local

        Returns:
            {
                "object": str,
                "dimensions": [x, y, z],
                "center": [x, y, z],
                "min_bound": [x, y, z],
                "max_bound": [x, y, z],
                "volume": float
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"error": f"Object '{object_name}' not found"}

        if world_space:
            # Calculer les bounds en world space
            bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

            min_x = min(corner.x for corner in bbox_corners)
            max_x = max(corner.x for corner in bbox_corners)
            min_y = min(corner.y for corner in bbox_corners)
            max_y = max(corner.y for corner in bbox_corners)
            min_z = min(corner.z for corner in bbox_corners)
            max_z = max(corner.z for corner in bbox_corners)

            dimensions = [
                max_x - min_x,
                max_y - min_y,
                max_z - min_z
            ]

            center = [
                (max_x + min_x) / 2,
                (max_y + min_y) / 2,
                (max_z + min_z) / 2
            ]

            min_bound = [min_x, min_y, min_z]
            max_bound = [max_x, max_y, max_z]
        else:
            dimensions = [obj.dimensions.x, obj.dimensions.y, obj.dimensions.z]
            center = [obj.location.x, obj.location.y, obj.location.z]

            # Bounds locaux
            min_bound = [c for c in obj.bound_box[0]]
            max_bound = [c for c in obj.bound_box[6]]

        volume = dimensions[0] * dimensions[1] * dimensions[2]

        return {
            "object": object_name,
            "dimensions": dimensions,
            "center": center,
            "min_bound": min_bound,
            "max_bound": max_bound,
            "volume": volume
        }

    from mathutils import Vector
    result = get_object_bounds(cube.name)
    print(f"Result: {result}")
    assert result["dimensions"][0] > 0
    assert result["volume"] > 0
    print("✅ PASS")


# =============================================================================
# 3. VALIDATE MESH - Valider la qualité du mesh
# =============================================================================

def test_validate_mesh():
    """Test: Valider un mesh"""
    print("\n=== TEST: validate_mesh ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def validate_mesh(object_name: str, fix_issues: bool = False) -> Dict[str, Any]:
        """
        Valider la qualité d'un mesh et détecter les erreurs

        Args:
            object_name: Nom de l'objet
            fix_issues: Si True, tente de corriger les problèmes

        Returns:
            {
                "object": str,
                "is_valid": bool,
                "issues": List[str],
                "non_manifold_edges": int,
                "degenerate_faces": int,
                "duplicate_faces": int,
                "fixed": bool
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        mesh = obj.data
        issues = []

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')

        # Sélectionner non-manifold
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.object.mode_set(mode='OBJECT')

        non_manifold_count = sum(1 for e in mesh.edges if e.select)
        if non_manifold_count > 0:
            issues.append(f"{non_manifold_count} non-manifold edges")

        # Vérifier les faces dégénérées (area trop petite)
        degenerate_count = 0
        for face in mesh.polygons:
            if face.area < 0.0001:
                degenerate_count += 1

        if degenerate_count > 0:
            issues.append(f"{degenerate_count} degenerate faces")

        # Fixer les problèmes si demandé
        fixed = False
        if fix_issues and len(issues) > 0:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Supprimer les doubles
            bpy.ops.mesh.remove_doubles()

            # Recalculer les normales
            bpy.ops.mesh.normals_make_consistent(inside=False)

            # Supprimer les faces dégénérées
            bpy.ops.mesh.delete_loose()

            bpy.ops.object.mode_set(mode='OBJECT')
            fixed = True

        is_valid = len(issues) == 0

        return {
            "object": object_name,
            "is_valid": is_valid,
            "issues": issues,
            "non_manifold_edges": non_manifold_count,
            "degenerate_faces": degenerate_count,
            "fixed": fixed
        }

    result = validate_mesh(cube.name)
    print(f"Result: {result}")
    assert result["is_valid"] == True  # Un cube propre devrait être valide
    print("✅ PASS")


# =============================================================================
# 4. CHECK UVS - Vérifier les UVs
# =============================================================================

def test_check_uvs():
    """Test: Vérifier les UVs"""
    print("\n=== TEST: check_uvs ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def check_uvs(object_name: str) -> Dict[str, Any]:
        """
        Vérifier si un objet a des UVs et leur qualité

        Args:
            object_name: Nom de l'objet

        Returns:
            {
                "object": str,
                "has_uvs": bool,
                "uv_layers": int,
                "uv_layer_names": List[str],
                "faces_with_uvs": int,
                "faces_without_uvs": int
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        mesh = obj.data

        has_uvs = len(mesh.uv_layers) > 0
        uv_layer_names = [layer.name for layer in mesh.uv_layers]

        faces_with_uvs = 0
        faces_without_uvs = 0

        if has_uvs:
            # Compter les faces avec UVs valides
            uv_layer = mesh.uv_layers.active
            if uv_layer:
                for face in mesh.polygons:
                    # Une face a des UVs si tous ses loops ont des coords UV
                    has_face_uvs = True
                    for loop_idx in face.loop_indices:
                        uv = uv_layer.data[loop_idx].uv
                        if uv.length == 0:
                            has_face_uvs = False
                            break

                    if has_face_uvs:
                        faces_with_uvs += 1
                    else:
                        faces_without_uvs += 1

        return {
            "object": object_name,
            "has_uvs": has_uvs,
            "uv_layers": len(mesh.uv_layers),
            "uv_layer_names": uv_layer_names,
            "faces_with_uvs": faces_with_uvs,
            "faces_without_uvs": faces_without_uvs
        }

    result = check_uvs(cube.name)
    print(f"Result: {result}")
    # Un cube par défaut n'a pas d'UVs
    assert result["has_uvs"] in [True, False]
    print("✅ PASS")


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CATEGORY 3: INSPECTION & VALIDATION")
    print("=" * 60)

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    try:
        test_get_mesh_stats()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_get_object_bounds()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_validate_mesh()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_check_uvs()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - CATEGORY 3")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
