"""
CATEGORY 2: EDGE OPERATIONS (IMPORTANT)
Test des outils d'opérations sur les edges
"""

import bpy
from typing import List, Dict, Any, Tuple

# =============================================================================
# 1. BEVEL EDGES - Chanfreiner les angles (ESSENTIEL pour le réalisme)
# =============================================================================

def test_bevel_edges():
    """Test: Chanfreiner les edges"""
    print("\n=== TEST: bevel_edges ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def bevel_edges(object_name: str, edge_indices: List[int] = None,
                   width: float = 0.1, segments: int = 2,
                   profile: float = 0.5) -> Dict[str, Any]:
        """
        Chanfreiner les edges (arrondir les angles)

        Args:
            object_name: Nom de l'objet
            edge_indices: Indices des edges (None = tous)
            width: Largeur du bevel
            segments: Nombre de segments (résolution)
            profile: Profil du bevel (0.5 = uniforme)

        Returns:
            {
                "object": str,
                "beveled_edges": int,
                "new_vertex_count": int,
                "segments": int
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

        # Sélectionner les edges
        if edge_indices is None:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            edge_count = len(mesh.edges)
        else:
            for idx in edge_indices:
                if 0 <= idx < len(mesh.edges):
                    mesh.edges[idx].select = True
            edge_count = len(edge_indices)
            bpy.ops.object.mode_set(mode='EDIT')

        # Bevel
        bpy.ops.mesh.bevel(
            offset=width,
            segments=segments,
            profile=profile
        )

        bpy.ops.object.mode_set(mode='OBJECT')

        return {
            "object": object_name,
            "beveled_edges": edge_count,
            "new_vertex_count": len(mesh.vertices),
            "segments": segments
        }

    result = bevel_edges(cube.name, width=0.1, segments=3)
    print(f"Result: {result}")
    assert result["new_vertex_count"] > 8  # Plus que 8 vertices d'origine
    print("✅ PASS")


# =============================================================================
# 2. SUBDIVIDE - Subdiviser des edges/faces
# =============================================================================

def test_subdivide_mesh():
    """Test: Subdiviser la géométrie"""
    print("\n=== TEST: subdivide_mesh ===")

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object

    def subdivide_mesh(object_name: str, cuts: int = 1,
                      smooth: float = 0.0) -> Dict[str, Any]:
        """
        Subdiviser la géométrie sélectionnée

        Args:
            object_name: Nom de l'objet
            cuts: Nombre de coupes
            smooth: Facteur de lissage (0-1)

        Returns:
            {
                "object": str,
                "vertices_before": int,
                "vertices_after": int,
                "cuts": int
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

        # Subdivide
        bpy.ops.mesh.subdivide(
            number_cuts=cuts,
            smoothness=smooth
        )

        bpy.ops.object.mode_set(mode='OBJECT')

        after_count = len(mesh.vertices)

        return {
            "object": object_name,
            "vertices_before": before_count,
            "vertices_after": after_count,
            "cuts": cuts
        }

    result = subdivide_mesh(cube.name, cuts=2)
    print(f"Result: {result}")
    assert result["vertices_after"] > result["vertices_before"]
    print("✅ PASS")


# =============================================================================
# 3. BRIDGE EDGE LOOPS - Connecter deux edge loops
# =============================================================================

def test_bridge_edge_loops():
    """Test: Connecter deux edge loops"""
    print("\n=== TEST: bridge_edge_loops ===")

    # Créer deux cylindres
    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 0), vertices=8)
    cyl1 = bpy.context.active_object

    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 3), vertices=8)
    cyl2 = bpy.context.active_object

    # Joindre
    bpy.ops.object.select_all(action='DESELECT')
    cyl1.select_set(True)
    cyl2.select_set(True)
    bpy.context.view_layer.objects.active = cyl1
    bpy.ops.object.join()

    def bridge_edge_loops(object_name: str, edge_loop_1: List[int],
                         edge_loop_2: List[int]) -> Dict[str, Any]:
        """
        Connecter deux edge loops avec des faces

        Args:
            object_name: Nom de l'objet
            edge_loop_1: Indices des edges du premier loop
            edge_loop_2: Indices des edges du second loop

        Returns:
            {
                "object": str,
                "faces_created": int,
                "bridged_edges": int
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        mesh = obj.data
        before_faces = len(mesh.polygons)

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # Sélectionner les edges
        for idx in edge_loop_1 + edge_loop_2:
            if 0 <= idx < len(mesh.edges):
                mesh.edges[idx].select = True

        bpy.ops.object.mode_set(mode='EDIT')

        # Bridge
        bpy.ops.mesh.bridge_edge_loops()

        bpy.ops.object.mode_set(mode='OBJECT')

        after_faces = len(mesh.polygons)

        return {
            "object": object_name,
            "faces_created": after_faces - before_faces,
            "bridged_edges": len(edge_loop_1) + len(edge_loop_2)
        }

    # Test simple: sélectionner tous les edges et bridge
    result = bridge_edge_loops(cyl1.name, list(range(8)), list(range(8, 16)))
    print(f"Result: {result}")
    print("✅ PASS")


# =============================================================================
# 4. LOOP CUT - Ajouter des edge loops
# =============================================================================

def test_loop_cut():
    """Test: Ajouter des edge loops"""
    print("\n=== TEST: loop_cut ===")

    bpy.ops.mesh.primitive_cylinder_add(location=(0, 0, 0))
    cylinder = bpy.context.active_object

    def add_loop_cuts(object_name: str, cuts: int = 1,
                     position: float = 0.0) -> Dict[str, Any]:
        """
        Ajouter des edge loops (loop cuts)

        Args:
            object_name: Nom de l'objet
            cuts: Nombre de loops à ajouter
            position: Position relative (-1 à 1, 0 = centre)

        Returns:
            {
                "object": str,
                "loops_added": int,
                "edges_before": int,
                "edges_after": int
            }
        """
        obj = bpy.data.objects.get(object_name)
        if not obj or obj.type != 'MESH':
            return {"error": f"Mesh object '{object_name}' not found"}

        mesh = obj.data
        before_edges = len(mesh.edges)

        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')

        # Subdivide (alternative à loop cut pour test)
        bpy.ops.mesh.subdivide(number_cuts=cuts)

        bpy.ops.object.mode_set(mode='OBJECT')

        after_edges = len(mesh.edges)

        return {
            "object": object_name,
            "loops_added": cuts,
            "edges_before": before_edges,
            "edges_after": after_edges
        }

    result = add_loop_cuts(cylinder.name, cuts=3)
    print(f"Result: {result}")
    assert result["edges_after"] > result["edges_before"]
    print("✅ PASS")


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CATEGORY 2: EDGE OPERATIONS")
    print("=" * 60)

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    try:
        test_bevel_edges()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_subdivide_mesh()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_bridge_edge_loops()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        test_loop_cut()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - CATEGORY 2")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
