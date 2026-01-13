# 🔬 WORKFLOW DE VALIDATION DES TOOLS

## Processus en 3 étapes

### ✅ ÉTAPE 1 : Test isolé dans Blender (OBLIGATOIRE)

Avant toute intégration, **tester chaque fonction individuellement** dans la console Python de Blender.

#### Comment tester :

1. Ouvrir Blender
2. Ouvrir la console Python (Window > Toggle System Console ou Scripting workspace)
3. Exécuter le fichier de test :

```python
# Charger et exécuter le fichier de test
exec(open(r"D:\Frigg\tools\test_category_1_mesh_editing.py").read())
```

#### Critères de validation :
- ✅ Aucune erreur Python
- ✅ Tous les `assert` passent
- ✅ Les objets sont créés/modifiés correctement dans la scène
- ✅ Le résultat visuel est correct

**❌ SI UN TEST ÉCHOUE** : Ne pas intégrer, corriger d'abord !

---

### ✅ ÉTAPE 2 : Test du bridge handler (OBLIGATOIRE)

Une fois les fonctions testées, tester le **handler du bridge**.

#### Fichier de test : `tools/test_bridge_handlers.py`

```python
"""
Test des bridge handlers via le système de commandes
"""

import json
import sys
import os

# Ajouter le chemin du bridge addon
BRIDGE_PATH = r"D:\Frigg\blender_bridge_addon"
sys.path.insert(0, BRIDGE_PATH)

import bpy

# Importer les handlers
from __init__ import COMMAND_HANDLERS

def test_handler(handler_name, command_data):
    """Tester un handler spécifique"""
    print(f"\n=== Testing handler: {handler_name} ===")
    print(f"Input: {json.dumps(command_data, indent=2)}")

    if handler_name not in COMMAND_HANDLERS:
        print(f"❌ Handler '{handler_name}' not found!")
        return False

    handler = COMMAND_HANDLERS[handler_name]

    try:
        result = handler(command_data)
        print(f"Result: {json.dumps(result, indent=2)}")

        if "error" in result:
            print(f"❌ Handler returned error: {result['error']}")
            return False

        print("✅ Handler executed successfully")
        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

# =============================================================================
# TESTS POUR BATCH 1 : MESH EDITING
# =============================================================================

def test_batch_1():
    """Test handlers for mesh editing tools"""
    print("\n" + "="*60)
    print("BATCH 1: MESH EDITING HANDLERS")
    print("="*60)

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Test 1: join_objects
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube1 = bpy.context.active_object
    cube1.name = "Cube1"

    bpy.ops.mesh.primitive_cube_add(location=(2, 0, 0))
    cube2 = bpy.context.active_object
    cube2.name = "Cube2"

    success = test_handler("join_objects", {
        "object_names": ["Cube1", "Cube2"],
        "result_name": "JoinedCubes"
    })

    if not success:
        return False

    # Test 2: extrude_faces
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    success = test_handler("extrude_faces", {
        "object_name": "TestCube",
        "face_indices": [5],  # Top face
        "offset": 0.5
    })

    if not success:
        return False

    # Test 3: inset_faces
    success = test_handler("inset_faces", {
        "object_name": "TestCube",
        "thickness": 0.1,
        "depth": 0.0
    })

    if not success:
        return False

    # Test 4: merge_vertices
    success = test_handler("merge_vertices", {
        "object_name": "TestCube",
        "distance": 0.001
    })

    if not success:
        return False

    print("\n✅ ALL BATCH 1 HANDLERS PASSED")
    return True

# =============================================================================
# TESTS POUR BATCH 2 : EDGE OPERATIONS
# =============================================================================

def test_batch_2():
    """Test handlers for edge operations"""
    print("\n" + "="*60)
    print("BATCH 2: EDGE OPERATIONS HANDLERS")
    print("="*60)

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Test 1: bevel_edges
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    success = test_handler("bevel_edges", {
        "object_name": "TestCube",
        "width": 0.1,
        "segments": 2
    })

    if not success:
        return False

    # Test 2: subdivide_mesh
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    success = test_handler("subdivide_mesh", {
        "object_name": "TestCube",
        "cuts": 2,
        "smooth": 0.0
    })

    if not success:
        return False

    print("\n✅ ALL BATCH 2 HANDLERS PASSED")
    return True

# =============================================================================
# TESTS POUR BATCH 3 : INSPECTION
# =============================================================================

def test_batch_3():
    """Test handlers for inspection tools"""
    print("\n" + "="*60)
    print("BATCH 3: INSPECTION HANDLERS")
    print("="*60)

    # Nettoyer la scène
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "TestCube"

    # Test 1: get_mesh_stats
    success = test_handler("get_mesh_stats", {
        "object_name": "TestCube"
    })

    if not success:
        return False

    # Test 2: get_object_bounds
    success = test_handler("get_object_bounds", {
        "object_name": "TestCube",
        "world_space": True
    })

    if not success:
        return False

    # Test 3: validate_mesh
    success = test_handler("validate_mesh", {
        "object_name": "TestCube",
        "fix_issues": False
    })

    if not success:
        return False

    # Test 4: check_uvs
    success = test_handler("check_uvs", {
        "object_name": "TestCube"
    })

    if not success:
        return False

    print("\n✅ ALL BATCH 3 HANDLERS PASSED")
    return True

# =============================================================================
# RUN ALL
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("BRIDGE HANDLERS VALIDATION")
    print("="*60)

    all_success = True

    if test_batch_1():
        print("✅ BATCH 1 OK")
    else:
        print("❌ BATCH 1 FAILED")
        all_success = False

    if test_batch_2():
        print("✅ BATCH 2 OK")
    else:
        print("❌ BATCH 2 FAILED")
        all_success = False

    if test_batch_3():
        print("✅ BATCH 3 OK")
    else:
        print("❌ BATCH 3 FAILED")
        all_success = False

    print("\n" + "="*60)
    if all_success:
        print("✅✅✅ ALL HANDLERS VALIDATED - READY FOR MCP INTEGRATION")
    else:
        print("❌❌❌ SOME HANDLERS FAILED - FIX BEFORE INTEGRATION")
    print("="*60)
```

---

### ✅ ÉTAPE 3 : Test MCP end-to-end (FINAL)

Une fois les handlers validés, tester via le **MCP complet**.

#### Fichier : `tools/test_mcp_integration.py`

```python
"""
Test end-to-end via MCP
Nécessite que le serveur MCP et le bridge soient en cours d'exécution
"""

import asyncio
import json

# Note: Ce fichier doit être exécuté depuis l'environnement MCP, pas Blender

async def test_mcp_tool(tool_name, params):
    """Test un outil MCP"""
    print(f"\n=== Testing MCP tool: {tool_name} ===")
    print(f"Params: {json.dumps(params, indent=2)}")

    # Import du module MCP
    from frigg_mcp.tools import mesh_editing_tools

    # Récupérer la fonction
    func = getattr(mesh_editing_tools, tool_name)

    try:
        result = await func(**params)
        print(f"Result: {json.dumps(result, indent=2)}")

        if "error" in result:
            print(f"❌ Tool returned error: {result['error']}")
            return False

        print("✅ Tool executed successfully")
        return True

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*60)
    print("MCP INTEGRATION TESTS")
    print("="*60)

    # Test join_objects
    success = await test_mcp_tool("frigg_blender_join_objects", {
        "object_names": ["Cube1", "Cube2"],
        "result_name": "JoinedCubes"
    })

    if success:
        print("✅ MCP INTEGRATION OK")
    else:
        print("❌ MCP INTEGRATION FAILED")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📋 CHECKLIST DE VALIDATION

Avant d'intégrer un batch de tools, vérifier :

### ☐ Phase 1 : Tests isolés
- [ ] Fichier `test_category_X.py` créé
- [ ] Tous les tests passent dans Blender console
- [ ] Résultats visuels corrects dans la scène 3D
- [ ] Aucune erreur Python levée

### ☐ Phase 2 : Tests handlers
- [ ] Handlers ajoutés à `blender_bridge_addon/__init__.py`
- [ ] Handlers ajoutés au dict `COMMAND_HANDLERS`
- [ ] `test_bridge_handlers.py` passe tous les tests
- [ ] JSON de retour valide et complet

### ☐ Phase 3 : Tests MCP
- [ ] Fichiers MCP tools créés dans `src/frigg_mcp/tools/`
- [ ] Imports ajoutés dans `__init__.py`
- [ ] Le serveur MCP démarre sans erreur
- [ ] Les outils apparaissent dans la liste MCP
- [ ] Test end-to-end réussi

### ☐ Phase 4 : Tests avec Claude
- [ ] Claude peut appeler les outils via MCP
- [ ] Les résultats sont corrects
- [ ] Pas de timeout ou d'erreur de connexion
- [ ] Documentation testée (docstrings accessibles)

---

## 🚨 RÈGLES D'OR

1. **JAMAIS d'intégration sans test** - Un outil non testé = bug garanti
2. **Tester dans l'ordre** - Isolé → Handler → MCP → Claude
3. **Un échec = STOP** - Corriger avant de continuer
4. **Garder les tests** - Ne pas supprimer, ils servent de régression
5. **Documenter les bugs** - Si un test échoue, noter pourquoi

---

## 🎯 RÉSUMÉ WORKFLOW

```
1. Codex génère le code
   ↓
2. Copier dans test_category_X.py
   ↓
3. Exécuter dans Blender console
   ↓ (si ✅)
4. Intégrer les handlers dans bridge addon
   ↓
5. Tester avec test_bridge_handlers.py
   ↓ (si ✅)
6. Créer les MCP tools
   ↓
7. Tester avec test_mcp_integration.py
   ↓ (si ✅)
8. Commiter et tester avec Claude
   ↓
9. ✅ DÉPLOIEMENT OK
```

**NE JAMAIS SAUTER D'ÉTAPE !** 🛑
