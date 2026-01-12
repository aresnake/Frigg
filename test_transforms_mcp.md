# Test Plan for set_object_rotation and set_object_scale via MCP

**Version:** v0.10
**Date:** 2026-01-12

---

## Test Cases

### Test 1: set_object_rotation - Basic Z rotation
```
Rotate the default Cube 45 degrees on the Z axis
```

**Expected:**
- Tool: `frigg.blender.set_object_rotation`
- Parameters: `{object_name: "Cube", rotation: [0, 0, 45]}`
- Result: Cube rotated 45° around Z axis
- Returns: rotation in degrees and radians

---

### Test 2: set_object_rotation - Multi-axis
```
Rotate the Cube to [30, 45, 60] degrees
```

**Expected:**
- Result: Cube rotated on all three axes
- Can verify with viewport_snapshot

---

### Test 3: set_object_scale - Uniform scale
```
Scale the Cube to 2x its original size
```

**Expected:**
- Tool: `frigg.blender.set_object_scale`
- Parameters: `{object_name: "Cube", scale: 2.0}`
- Result: Cube doubled in all dimensions

---

### Test 4: set_object_scale - Non-uniform scale
```
Scale the Cube to be stretched: [1, 1, 3] (tall and narrow)
```

**Expected:**
- Result: Cube stretched 3x on Z axis only
- Original dimensions on X and Y

---

### Test 5: Combined transforms
```
1. Reset Cube to origin: location [0, 0, 0]
2. Scale it to 1.5
3. Rotate it 45 degrees on Z
4. Move it to [2, 0, 1]
5. Take a viewport snapshot to verify
```

**Expected:**
- All transforms applied correctly
- Snapshot shows transformed cube

---

### Test 6: Verify with get_object_transform
```
After applying transforms, use get_object_transform to read back the values
```

**Expected:**
- Returns match what was set
- Can verify rotation, scale, location

---

## Notes

- Both tools should be visible in Claude Desktop MCP tool list
- Should work without requiring bridge restart (already restarted)
- Test in fresh Blender scene with default Cube

## Status

- [ ] Test 1: Basic rotation
- [ ] Test 2: Multi-axis rotation
- [ ] Test 3: Uniform scale
- [ ] Test 4: Non-uniform scale
- [ ] Test 5: Combined transforms
- [ ] Test 6: Read back transforms
