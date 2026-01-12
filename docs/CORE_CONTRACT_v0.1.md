# FRIGG MCP CORE CONTRACT v0.1

This document defines the locked CORE tool contract for FRIGG MCP v0.1.

Only the 12 CORE tools below appear in `tools/list`. L2 and other non-core tools may exist in code but are intentionally hidden from `tools/list`.

## Response envelope

All tool calls return a unified envelope:

Success:
```json
{
  "ok": true,
  "result": {}
}
```

Error:
```json
{
  "ok": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Tools and input schemas

1) `frigg.ping`
```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

2) `frigg.blender.bridge_ping`
```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

3) `frigg.blender.get_scene_info`
```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

4) `frigg.blender.list_objects`
```json
{
  "type": "object",
  "properties": {},
  "required": [],
  "additionalProperties": false
}
```

5) `frigg.blender.create_primitive`
```json
{
  "type": "object",
  "properties": {
    "type": {
      "type": "string",
      "enum": ["CUBE", "SPHERE", "CYLINDER", "CONE", "TORUS", "PLANE", "MONKEY"]
    },
    "name": { "type": "string" },
    "location": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 3,
      "maxItems": 3
    },
    "rotation": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 3,
      "maxItems": 3
    },
    "scale": {
      "oneOf": [
        { "type": "number" },
        {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 3,
          "maxItems": 3
        }
      ]
    },
    "size": { "type": "number", "minimum": 0 }
  },
  "required": ["type"],
  "additionalProperties": false
}
```

6) `frigg.blender.delete_object`
```json
{
  "type": "object",
  "properties": { "name": { "type": "string" } },
  "required": ["name"],
  "additionalProperties": false
}
```

7) `frigg.blender.select_object`
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "action": { "type": "string", "enum": ["SET", "ADD", "REMOVE", "TOGGLE"] }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

8) `frigg.blender.get_transform`
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "space": { "type": "string", "enum": ["LOCAL", "WORLD"] }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

9) `frigg.blender.set_transform`
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "space": { "type": "string", "enum": ["LOCAL", "WORLD"] },
    "location": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 3,
      "maxItems": 3
    },
    "rotation": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 3,
      "maxItems": 3
    },
    "rotation_mode": { "type": "string", "enum": ["DEGREES", "RADIANS"] },
    "scale": {
      "oneOf": [
        { "type": "number" },
        {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 3,
          "maxItems": 3
        }
      ]
    }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

10) `frigg.blender.apply_transform`
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "apply_location": { "type": "boolean" },
    "apply_rotation": { "type": "boolean" },
    "apply_scale": { "type": "boolean" }
  },
  "required": ["name"],
  "additionalProperties": false
}
```

11) `frigg.blender.create_camera`
```json
{
  "type": "object",
  "properties": {
    "name": { "type": "string" },
    "location": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 3,
      "maxItems": 3
    },
    "rotation": {
      "type": "array",
      "items": { "type": "number" },
      "minItems": 3,
      "maxItems": 3
    },
    "projection": { "type": "string", "enum": ["PERSP", "ORTHO"] },
    "focal_length": { "type": "number", "minimum": 0 },
    "ortho_scale": { "type": "number", "minimum": 0 }
  },
  "required": [],
  "additionalProperties": false
}
```

12) `frigg.blender.set_active_camera`
```json
{
  "type": "object",
  "properties": { "name": { "type": "string" } },
  "required": ["name"],
  "additionalProperties": false
}
```
