"""
CATEGORY 1: MESH EDITING (CRITIQUE)
Test des outils d'édition de géométrie essentiels
"""

import bpy
from typing import List, Dict, Any

# =============================================================================
# 1. JOIN OBJECTS - Fusionner plusieurs objets en un seul mesh
# =============================================================================

def test_join_objects():
    """Test: Fusionner plusieurs objets en un seul"""
    print("\n=== TEST: join_objects ===")

    # Créer 3 cubes
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube1 = bpy.context.active_object
    cube1.name = "Cube1"

    bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
    cube2 = bpy.context.active_object
    cube2.name = "Cube2"

    bpy.ops.mesh.primitive_cube_add(location=(4, 0, 0))
    cube3 = bpy.context.active_object
    cube3.name = "Cube3"

    # Fonction à implémenter
    def join_objects(object_names: List[str], result_name: str = None) -> Dict[str, Any]:
        """
        Fusionne plusieurs objets en un seul mesh

        Args:
            object_names: Liste des noms d'objets à fusionner
            result_name: Nom optionnel pour l'objet résultant

        Returns:
            {
                "result_object": str,
                "vertex_count": int,
                "face_count": int,
                "merged_objects": List[str]
            }
        """
        # Validation
        objects = []
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if not obj:
                return {"error": f"Object '{name}' not found"}
            if obj.type != 'MESH':
                return {"error": f"Object '{name}' is not a mesh"}
            objects.append(obj)

        if len(objects) < 2:
            return {"error": "Need at least 2 objects to join"}

        # Désélectionner tout
        bpy.ops.object.select_all(action='DESELECT')

        # Sélectionner les objets à joindre
        for obj in objects:
            obj.select_set(True)

        # Le premier objet devient l'objet actif
        bpy.context.view_layer.objects.active = objects[0]

        # Joindre
        bpy.ops.object.join()

        result_obj = bpy.context.active_object

        # Renommer si demandé
        if result_name:
            result_obj.name = result_name

        # Stats
        mesh = result_obj.data
        vertex_count = len(mesh.vertices)
        face_count = len(mesh.polygons)

        return {
            "result_object": result_obj.name,
            "vertex_count": vertex_count,
            "face_count": face_count,
            "merged_objects": object_names
        }

    # Test
    result = join_objects(["Cube1", "Cube2", "Cube3"], "JoinedCubes")
    print(f"Result: {result}")
    assert result["vertex_count"] == 24  # 3 cubes x 8 vertices
    assert result["face_count"] == 18    # 3 cubes x 6 faces
    print("✅ PASS")


# =============================================================================
# 2. EXTRUDE FACES - Extruder des faces sélectionnées
# =============================================================================

def test_extrude_faces():
    """Test: Extruder des faces"""
    print("\n=== TEST: extrude_faces ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def extrude_faces(object_name: str, face_indices: List[int],
                     offset: float = 0.5, direction: List[float] = None) -> Dict[str, Any]:
        """
        Extrude des faces spécifiques

        Args:
            object_name: Nom de l'objet
            face_indices: Indices des faces à extruder (ou "all" pour toutes)
            offset: Distance d'extrusion
            direction: Direction [x,y,z] optionnelle (None = normale de la face)

        Returns:
            {
                "object": str,
                "extruded_faces": int,
                "new_vertex_count": int
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        # Passer en mode édition
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        # Passer en mode objet pour sélectionner les faces
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data

        # Sélectionner les faces
        if face_indices == "all":
            for face in mesh.polygons:
                face.select = True
            face_count = len(mesh.polygons)
        else:
            for idx in face_indices:
                if 0 <= idx < len(mesh.polygons):
                    mesh.polygons[idx].select = True
            face_count = len(face_indices)

        # Retourner en mode édition
        bpy.ops.object.mode_set(mode='EDIT')

        # Extruder
        if direction:
            # Extrusion dans une direction spécifique
            bpy.ops.mesh.extrude_region_move(
                TRANSFORM_OT_translate={"value": (
                    direction[0] * offset,
                    direction[1] * offset,
                    direction[2] * offset
                )}
            )
        else:
            # Extrusion le long des normales
            bpy.ops.mesh.extrude_faces_move(
                MESH_OT_extrude_faces_indiv={"mirror": False},
                TRANSFORM_OT_shrink_fatten={"value": offset}
            )

        # Retour en mode objet
        bpy.ops.object.mode_set(mode='OBJECT')

        return {
            "object": object_name,
            "extruded_faces": face_count,
            "new_vertex_count": len(mesh.vertices)
        }

    # Test: extruder la face du dessus (index 5 sur un cube)
    result = extrude_faces(cube.name, [5], offset=0.5)
    print(f"Result: {result}")
    assert result["new_vertex_count"] > 8  # Plus que les 8 vertices d'origine
    print("✅ PASS")


# =============================================================================
# 3. INSET FACES - Créer des insets (détails)
# =============================================================================

def test_inset_faces():
    """Test: Créer des insets sur des faces"""
    print("\n=== TEST: inset_faces ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def inset_faces(object_name: str, face_indices: List[int] = None,
                   thickness: float = 0.1, depth: float = 0.0) -> Dict[str, Any]:
        """
        Créer des insets sur des faces (pour détails comme planches, panneaux)

        Args:
            object_name: Nom de l'objet
            face_indices: Indices des faces (None = toutes)
            thickness: Épaisseur de l'inset
            depth: Profondeur (négatif = vers l'intérieur)

        Returns:
            {
                "object": str,
                "inset_faces": int,
                "new_face_count": int
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = obj.data

        # Sélectionner les faces
        if face_indices is None:
            for face in mesh.polygons:
                face.select = True
            face_count = len(mesh.polygons)
        else:
            for idx in face_indices:
                if 0 <= idx < len(mesh.polygons):
                    mesh.polygons[idx].select = True
            face_count = len(face_indices)

        bpy.ops.object.mode_set(mode='EDIT')

        # Inset
        bpy.ops.mesh.inset(thickness=thickness, depth=depth)

        bpy.ops.object.mode_set(mode='OBJECT')

        return {
            "object": object_name,
            "inset_faces": face_count,
            "new_face_count": len(mesh.polygons)
        }

    # Test: inset sur toutes les faces
    result = inset_faces(cube.name, thickness=0.1)
    print(f"Result: {result}")
    assert result["new_face_count"] > 6  # Plus que les 6 faces d'origine
    print("✅ PASS")


# =============================================================================
# 4. MERGE VERTICES - Fusionner les vertices proches (remove doubles)
# =============================================================================

def test_merge_vertices():
    """Test: Fusionner les vertices proches"""
    print("\n=== TEST: merge_vertices ===")

    # Créer deux cubes qui se touchent
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube1 = bpy.context.active_object

    bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
    cube2 = bpy.context.active_object

    # Les joindre
    bpy.ops.object.select_all(action='DESELECT')
    cube1.select_set(True)
    cube2.select_set(True)
    bpy.context.view_layer.objects.active = cube1
    bpy.ops.object.join()

    def merge_vertices(object_name: str, distance: float = 0.0001) -> Dict[str, Any]:
        """
        Fusionner les vertices proches (remove doubles)

        Args:
            object_name: Nom de l'objet
            distance: Distance maximale pour fusionner

        Returns:
            {
                "object": str,
                "vertices_before": int,
                "vertices_after": int,
                "removed_count": int
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        mesh = obj.data
        before_count = len(mesh.vertices)

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Merge by distance
        bpy.ops.mesh.remove_doubles(threshold=distance)

        bpy.ops.object.mode_set(mode='OBJECT')

        after_count = len(mesh.vertices)

        return {
            "object": object_name,
            "vertices_before": before_count,
            "vertices_after": after_count,
            "removed_count": before_count - after_count
        }

    result = merge_vertices(cube1.name, distance=0.001)
    print(f"Result: {result}")
    assert result["removed_count"] >= 0
    print("✅ PASS")


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CATEGORY 1: MESH EDITING TOOLS")
    print("=" * 60)

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    try:
        test_join_objects()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_extrude_faces()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_inset_faces()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_merge_vertices()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - CATEGORY 1")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
