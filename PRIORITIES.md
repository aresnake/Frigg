# Frigg MCP - Immediate Priorities

**Last Updated:** 2026-01-11
**Current Version:** 0.1.4
**Next Version:** 0.7.0

---

## 🎯 Top 3 Priorities (Next 7 Days)

### Priority 1: Object Rotation Operations ⭐⭐⭐
**Why:** Complète la manipulation d'objets de base (location done, rotation next, scale after)
**Impact:** HIGH - Demande fréquente, cas d'usage critiques
**Effort:** MEDIUM (2-3 heures)

**Tasks:**
- [ ] Add `frigg.blender.set_rotation_euler` tool
- [ ] Add `frigg.blender.rotate_object` tool (relative rotation)
- [ ] Tests for both tools
- [ ] Update documentation

**Expected tools:**
```python
# Set absolute rotation
set_rotation_euler(name="Cube", rotation=[0, 0, 45])  # degrees

# Rotate relative
rotate_object(name="Cube", rotation=[0, 0, 10])  # rotate 10° around Z
```

---

### Priority 2: Object Scale Operations ⭐⭐⭐
**Why:** Complète le "transform trio" (location, rotation, scale)
**Impact:** HIGH - Ensemble complet de transformations
**Effort:** LOW (1-2 heures)

**Tasks:**
- [ ] Add `frigg.blender.set_scale` tool
- [ ] Add `frigg.blender.scale_object` tool (relative)
- [ ] Tests for both tools
- [ ] Update documentation

**Expected tools:**
```python
# Set absolute scale
set_scale(name="Cube", scale=[2, 2, 2])  # 2x bigger

# Scale relative
scale_object(name="Cube", factor=1.5)  # 50% bigger
```

---

### Priority 3: Basic Material System ⭐⭐⭐
**Why:** Les objets ont besoin de couleurs/matériaux pour être visibles
**Impact:** VERY HIGH - Requis pour tout workflow visuel
**Effort:** MEDIUM-HIGH (4-5 heures)

**Tasks:**
- [ ] Add `frigg.blender.create_material` tool
- [ ] Add `frigg.blender.assign_material` tool
- [ ] Add `frigg.blender.set_material_color` tool
- [ ] Add `frigg.blender.set_material_metallic` tool
- [ ] Add `frigg.blender.set_material_roughness` tool
- [ ] Tests for all material tools
- [ ] Update documentation with examples

**Expected tools:**
```python
# Create material
create_material(name="RedMetal")

# Assign to object
assign_material(object_name="Cube", material_name="RedMetal")

# Set properties
set_material_color(material_name="RedMetal", color=[1.0, 0.0, 0.0, 1.0])
set_material_metallic(material_name="RedMetal", value=0.8)
set_material_roughness(material_name="RedMetal", value=0.2)
```

---

## 🚀 Next Sprint (7-14 Days)

### Priority 4: Object Creation ⭐⭐
**Why:** Créer des objets de base sans UI
**Impact:** HIGH - Fondamental pour workflows procéduraux
**Effort:** MEDIUM (3-4 heures)

**Tools to add:**
- [ ] `create_cube`
- [ ] `create_sphere`
- [ ] `create_cylinder`
- [ ] `create_cone`
- [ ] `create_plane`
- [ ] `create_empty`

---

### Priority 5: Object Deletion ⭐⭐
**Why:** Nettoyer la scène
**Impact:** MEDIUM - Utile mais pas critique
**Effort:** LOW (1 hour)

**Tools to add:**
- [ ] `delete_object`
- [ ] `delete_objects` (batch)

---

### Priority 6: Camera Positioning ⭐⭐
**Why:** Configurer vues pour rendu
**Impact:** HIGH - Critique pour rendering workflows
**Effort:** MEDIUM (2-3 heures)

**Tools to add:**
- [ ] `set_camera_location`
- [ ] `set_camera_rotation`
- [ ] `camera_look_at` (point vers objet)
- [ ] `set_active_camera`

---

## 📊 Success Criteria

### v0.7.0 Goals (Target: 7 days)
- ✅ Rotation operations (2 tools)
- ✅ Scale operations (2 tools)
- ✅ Basic materials (5 tools)
- ✅ All tests passing
- ✅ Documentation updated

**Total new tools:** 9
**New capabilities:** Complete transform control + basic materials

---

### v0.8.0 Goals (Target: 14 days)
- ✅ Object creation (6 tools)
- ✅ Object deletion (2 tools)
- ✅ Camera positioning (4 tools)
- ✅ All tests passing
- ✅ Tutorial: "Create a scene from scratch"

**Total new tools:** 12 (cumulative: 28 tools)
**New capabilities:** Full scene creation workflow

---

## 🎬 Demo Scenario (v0.8.0)

**Goal:** Claude creates a complete scene from scratch

```
User: "Create a simple scene with a red metallic cube on a blue plane,
       with proper lighting and camera"

Claude uses:
1. create_plane() → Ground
2. set_scale("Plane", [10, 10, 1]) → Bigger ground
3. create_material("Blue") → Ground material
4. set_material_color("Blue", [0.2, 0.3, 1.0, 1.0])
5. assign_material("Plane", "Blue")
6. create_cube() → Main object
7. set_location("Cube", [0, 0, 1]) → Above ground
8. create_material("RedMetal") → Cube material
9. set_material_color("RedMetal", [1.0, 0.1, 0.1, 1.0])
10. set_material_metallic("RedMetal", 0.9)
11. set_material_roughness("RedMetal", 0.1)
12. assign_material("Cube", "RedMetal")
13. set_camera_location([7, -7, 5])
14. camera_look_at("Cube")
15. scene_info() → Verify all is good

Result: Complete, beautiful scene in 15 tool calls!
```

---

## 💡 Quick Wins (Can be done anytime)

### Improve Error Messages
- [ ] Add "Did you mean?" suggestions for typos
- [ ] Better error messages for common mistakes
- [ ] Link to documentation in errors

### Performance
- [ ] Profile tool execution times
- [ ] Add timing logs (debug mode)
- [ ] Identify bottlenecks

### Documentation
- [ ] Create "Getting Started" tutorial video
- [ ] Add screenshots to README
- [ ] Create example gallery (rendered images)

### Developer Experience
- [ ] Add `--version` flag to MCP server
- [ ] Add `--help` flag
- [ ] Better startup messages

---

## 🤔 Technical Debt

### Must Fix Soon
- [ ] Add type stubs (.pyi files) for better IDE support
- [ ] Set up pre-commit hooks (black, mypy, ruff)
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Set up code coverage tracking

### Nice to Have
- [ ] Convert to async/await architecture
- [ ] Add connection pooling
- [ ] Implement request batching
- [ ] Add prometheus metrics

---

## 📈 Metrics to Track

### Usage Metrics (once public)
- Downloads per week
- Active users per month
- Average tools per session
- Most used tools

### Code Metrics
- Test coverage: >95%
- Lines of code
- Number of tools
- Documentation coverage

### Community Metrics
- GitHub stars
- Issues opened/closed
- Pull requests
- Contributors

---

## 🎯 Decision Framework

**When prioritizing new features, ask:**

1. **Impact:** How many users need this?
   - Critical (everyone) → HIGH
   - Important (many) → MEDIUM
   - Nice (few) → LOW

2. **Effort:** How long to implement?
   - <2 hours → LOW
   - 2-8 hours → MEDIUM
   - >8 hours → HIGH

3. **Dependencies:** What else is needed first?
   - Nothing → Can start now
   - One thing → Wait for that
   - Multiple → Plan carefully

4. **Innovation:** Does this differentiate us?
   - Unique feature → HIGH value
   - Common feature → MEDIUM value
   - Basic feature → LOW value (but might be required)

**Priority Matrix:**
```
High Impact + Low Effort = DO NOW ✅
High Impact + High Effort = PLAN CAREFULLY 📋
Low Impact + Low Effort = QUICK WIN 🎯
Low Impact + High Effort = DEFER ⏸️
```

---

## 🚫 What NOT to Do (Yet)

### Don't Start Until v1.0:
- ❌ Geometry Nodes (complex, needs foundation first)
- ❌ Python script execution (security concerns)
- ❌ Cloud rendering (infrastructure heavy)
- ❌ Multi-agent workflows (R&D phase)

### Don't Optimize Prematurely:
- ❌ Connection pooling (not needed yet)
- ❌ Request batching (not needed yet)
- ❌ Caching (measure first)

### Don't Over-Engineer:
- ❌ Plugin system (wait for community)
- ❌ Config file (env vars work fine)
- ❌ Web dashboard (CLI is enough)

**Focus:** Get to v0.9 with solid basics first!

---

## 📞 Questions to Answer

### Architecture Questions:
- [ ] Should we support Blender 4.x? (or only 5.x?)
- [ ] Should we support macOS/Linux? (currently Windows only)
- [ ] Should we support remote Blender? (currently localhost only)

### API Design Questions:
- [ ] Use degrees or radians for rotations? (degrees more intuitive)
- [ ] Use RGBA [0-1] or RGB [0-255]? (0-1 matches Blender)
- [ ] Sync or async by default? (sync for now, async later)

### Community Questions:
- [ ] When to open source? (after v0.9 with solid foundation)
- [ ] Which license? (MIT or Apache 2.0)
- [ ] Where to host docs? (ReadTheDocs or GitHub Pages)

---

## ✅ Action Items for Today

**If you have 1 hour:**
1. Implement `set_rotation_euler` tool
2. Add tests
3. Update docs
4. Commit: "feat(v0.7): add rotation control"

**If you have 2 hours:**
1. Do above ↑
2. Implement `set_scale` tool
3. Add tests
4. Commit: "feat(v0.7): complete transform trio (location, rotation, scale)"

**If you have 4 hours:**
1. Do above ↑
2. Implement basic material tools
3. Add tests
4. Create example: "Red metallic cube demo"
5. Commit: "feat(v0.7): add material system"
6. Tag release: `v0.7.0`

---

## 🎊 Celebration Milestones

- 🎉 v0.7: Transform trio complete → Tweet about it
- 🎉 v0.8: Full scene creation → Make demo video
- 🎉 v0.9: 30+ tools → Blog post
- 🎉 v1.0: Public launch → Submit to Anthropic showcase
- 🎉 100 GitHub stars → Special README badge
- 🎉 1000 GitHub stars → Contributor call + roadmap vote

---

**Remember:** "Perfect is the enemy of good." Ship early, iterate fast! 🚀
