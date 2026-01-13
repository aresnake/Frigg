# Frigg Modeling Tools - Gap Analysis
Date: 2026-01-13

## Executive Summary

Après une session de modélisation pratique créant des assets réels (table, crate, porte, boîte avec découpes), nous avons identifié **10 outils manquants** qui amélioreraient significativement les capacités de modélisation de Frigg.

## Assets Créés (Tests Réels)

1. ✅ **Table Simple** - Plateau + 4 pieds cylindriques
2. ✅ **Crate** - Cube avec détails inset
3. ✅ **Porte** - Cadre avec panneaux
4. ✅ **Boîte Détaillée** - Découpes boolean pour poignées
5. ✅ **Assemblage** - Fusion de composants multiples

## Outils Manquants Identifiés

### 🔴 HIGH PRIORITY (3 outils)

#### 1. `bevel_edges`
**Raison:** Essentiel pour le hard-surface modeling, arrondir les bords

**Use cases concrets:**
- Crates avec bords arrondis (réalisme)
- Meubles avec coins non-vifs
- Props mécaniques
- Amélioration visuelle générale

**Impact:** CRITIQUE pour assets professionnels

**Implémentation:**
```python
def bevel_edges(params):
    """Bevel edges on a mesh object."""
    - object_name: str
    - edge_indices: list[int] | "all"
    - width: float (default: 0.1)
    - segments: int (default: 2)
    - profile: float (0-1, default: 0.5)
```

---

#### 2. `subdivide_mesh`
**Raison:** Ajouter de la densité géométrique pour formes organiques

**Use cases concrets:**
- Modèles organiques nécessitant plus de détails
- Surfaces lisses
- Terrain
- Préparation pour sculpting

**Impact:** CRITIQUE pour modélisation organique

**Implémentation:**
```python
def subdivide_mesh(params):
    """Subdivide mesh faces."""
    - object_name: str
    - cuts: int (default: 1)
    - smooth: float (0-1, default: 0.0)
    - fractal: float (default: 0.0)
    - face_indices: list[int] | None
```

---

#### 3. `recalculate_normals`
**Raison:** Corriger les faces inversées (inside-out)

**Use cases concrets:**
- Nettoyage de TOUS les modèles
- Correction après boolean operations
- Import de modèles externes
- Préparation pour export

**Impact:** CRITIQUE pour qualité et rendu correct

**Implémentation:**
```python
def recalculate_normals(params):
    """Recalculate face normals (fix inside-out faces)."""
    - object_name: str
    - inside: bool (default: False)
```

---

### 🟡 MEDIUM PRIORITY (5 outils)

#### 4. `loop_cut`
**Raison:** Ajouter des edge loops pour topologie contrôlée

**Use cases:**
- Character modeling
- Déformation contrôlée
- Topologie propre

**Implémentation:**
```python
def loop_cut(params):
    """Add edge loop to mesh."""
    - object_name: str
    - edge_index: int
    - number_cuts: int (default: 1)
    - smoothness: float (default: 0.0)
```

---

#### 5. `select_by_normal`
**Raison:** Sélectionner faces par direction (haut, bas, etc.)

**Use cases:**
- Opérations batch automatiques
- Sélection de toits/sols
- Workflows procéduraux

**Implémentation:**
```python
def select_by_normal(params):
    """Select faces by normal direction."""
    - object_name: str
    - direction: [x, y, z]
    - threshold: float (angle tolerance)
    - extend: bool (add to selection)
```

---

#### 6. `bridge_edge_loops`
**Raison:** Connecter deux edge loops

**Use cases:**
- Remplir trous
- Connexions complexes
- Modélisation architecturale

**Implémentation:**
```python
def bridge_edge_loops(params):
    """Bridge two edge loops."""
    - object_name: str
    - loop1_edges: list[int]
    - loop2_edges: list[int]
    - cuts: int (default: 0)
    - smoothness: float
```

---

#### 7. `apply_all_modifiers`
**Raison:** Appliquer tous les modifiers d'un coup

**Use cases:**
- Finaliser modèles
- Batch operations
- Export préparation

**Implémentation:**
```python
def apply_all_modifiers(params):
    """Apply all modifiers on an object."""
    - object_name: str
    - types: list[str] | None (filter by type)
```

---

#### 8. `shade_smooth`
**Raison:** Définir smooth/flat shading

**Use cases:**
- Qualité visuelle
- Présentation
- Rendu

**Implémentation:**
```python
def shade_smooth(params):
    """Set smooth or flat shading."""
    - object_name: str
    - smooth: bool (True=smooth, False=flat)
    - auto_smooth: bool (default: False)
    - angle: float (auto smooth angle)
```

---

### 🟢 LOW PRIORITY (2 outils)

#### 9. `solidify_modifier`
**Note:** Déjà disponible via `add_modifier`, mais pourrait avoir une interface dédiée

**Use cases:**
- Objets shell (thickness)
- Murs, panneaux

---

#### 10. `triangulate`
**Raison:** Convertir en triangles pour export

**Use cases:**
- Game assets
- Export pour moteurs 3D
- Préparation FBX/glTF

**Implémentation:**
```python
def triangulate(params):
    """Triangulate mesh faces."""
    - object_name: str
    - quad_method: str ("BEAUTY", "FIXED", "ALTERNATE", "SHORT_EDGE")
    - ngon_method: str ("BEAUTY", "CLIP")
```

---

## Statistiques

### Priorités
- 🔴 HIGH: 3 outils (30%)
- 🟡 MEDIUM: 5 outils (50%)
- 🟢 LOW: 2 outils (20%)

### Catégories
- **Mesh Editing:** 6 outils (bevel, subdivide, loop_cut, bridge, triangulate, recalculate_normals)
- **Selection:** 1 outil (select_by_normal)
- **Modifiers:** 2 outils (apply_all, solidify dedicated)
- **Shading:** 1 outil (shade_smooth)

## Recommandations

### Phase 1 - Essentiels (HIGH)
Implémenter en priorité:
1. `bevel_edges` - Impact immédiat sur qualité visuelle
2. `recalculate_normals` - Nécessaire pour tous les workflows
3. `subdivide_mesh` - Ouvre la modélisation organique

**Estimation:** ~4-6 heures de développement + tests

### Phase 2 - Amélioration (MEDIUM)
1. `shade_smooth` - Simple mais très utilisé
2. `apply_all_modifiers` - Efficacité workflow
3. `loop_cut` - Topologie avancée
4. `select_by_normal` - Automatisation
5. `bridge_edge_loops` - Cas spéciaux

**Estimation:** ~6-8 heures de développement + tests

### Phase 3 - Bonus (LOW)
1. `triangulate` - Export seulement
2. Interface dédiée `solidify` - Déjà possible

**Estimation:** ~2-3 heures

## Impact sur Workflows

### Actuellement Possible ✅
- Primitives basiques
- Extrusion de faces
- Insets pour détails
- Boolean operations
- Fusion d'objets
- Collections
- Matériaux PBR

### Bloqué Sans Nouveaux Tools ❌
- Hard-surface détaillé (pas de bevel)
- Modélisation organique (pas de subdivide)
- Nettoyage automatique (pas de recalculate normals)
- Topologie contrôlée (pas de loop cuts)

### Amélioré Avec Nouveaux Tools ⬆️
- Qualité visuelle professionnelle
- Workflows plus rapides
- Automatisation possible
- Export production-ready

## Assets Testés

### Table ✅
**Créée avec:**
- create_primitive (cube + cylindres)
- scale transformations

**Pourrait bénéficier de:**
- bevel_edges (arrondir bords du plateau)
- shade_smooth (jambes lisses)

---

### Crate ✅
**Créée avec:**
- create_primitive (cube)
- inset_faces (détails de panneaux)

**Pourrait bénéficier de:**
- bevel_edges (coins arrondis réalistes)
- subdivide_mesh (plus de détails)
- recalculate_normals (après insets)

---

### Door ✅
**Créée avec:**
- create_primitive (cube)
- inset_faces (panneaux)

**Pourrait bénéficier de:**
- loop_cut (diviser en panneaux)
- bevel_edges (cadre détaillé)
- subdivide_mesh (détails panneaux)

---

### Detailed Box ✅
**Créée avec:**
- create_primitive (cubes + cylindres)
- boolean_operation (découpes)

**Pourrait bénéficier de:**
- bevel_edges (arrondir bords après boolean)
- recalculate_normals (corriger après boolean)
- apply_all_modifiers (finaliser)

---

## Conclusion

L'analyse pratique montre que Frigg possède une **base solide** mais a besoin de **3 outils critiques** (bevel, subdivide, recalculate_normals) pour passer à un niveau professionnel.

Les 24 outils actuels permettent de créer des assets basiques, mais les 10 outils identifiés débloqueraient:
- Hard-surface modeling professionnel
- Modélisation organique
- Nettoyage et finition automatique
- Workflows production-ready

**Recommandation:** Prioriser Phase 1 (3 outils HIGH) pour impact maximum immédiat.

---

**Next Steps:**
1. Implémenter les 3 outils HIGH priority
2. Tester avec assets plus complexes
3. Itérer sur MEDIUM priority selon besoins

**Status:** Analysis Complete - Ready for Implementation
