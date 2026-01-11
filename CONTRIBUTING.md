# Contributing to Frigg MCP

First off, thank you for considering contributing to Frigg! It's people like you who will make Frigg the best Blender MCP in the world. 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Testing Guidelines](#testing-guidelines)

---

## Code of Conduct

This project adheres to a Code of Conduct that we expect all contributors to follow:

- **Be respectful** - Treat everyone with respect and professionalism
- **Be collaborative** - Work together to achieve common goals
- **Be inclusive** - Welcome contributors from all backgrounds
- **Be constructive** - Provide helpful feedback and criticism
- **Be patient** - Remember that everyone is learning

Unacceptable behavior includes harassment, discrimination, or any form of abuse. Violations will result in removal from the project.

---

## How Can I Contribute?

### 🐛 Reporting Bugs

Before submitting a bug report:
1. Check the [existing issues](https://github.com/yourorg/frigg/issues)
2. Try to reproduce with the latest version
3. Gather relevant information (logs, OS version, Blender version)

**Good bug report includes:**
- Clear title (e.g., "set_location fails for non-existent object")
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs
- Environment details (OS, Python version, Blender version)

**Use the bug report template:**
```markdown
**Description:**
Clear description of the bug

**Steps to Reproduce:**
1. Start Frigg bridge
2. Call tool X with parameters Y
3. Observe error Z

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Windows 11
- Python: 3.11.0
- Blender: 5.0
- Frigg: 0.4.0

**Logs:**
```
[paste relevant logs]
```
```

### 💡 Suggesting Features

We love feature suggestions! Before submitting:
1. Check [ROADMAP.md](./ROADMAP.md) - might already be planned
2. Check [existing issues](https://github.com/yourorg/frigg/issues?q=is%3Aissue+label%3Aenhancement)
3. Think about:
   - Who needs this feature?
   - What problem does it solve?
   - Are there alternatives?

**Good feature request includes:**
- Clear use case ("As a 3D artist, I want to...")
- Problem description
- Proposed solution
- Alternative solutions considered
- Examples from other tools (if applicable)

### 📝 Improving Documentation

Documentation is crucial! You can help by:
- Fixing typos or unclear explanations
- Adding examples
- Translating to other languages (future)
- Creating tutorials or videos
- Improving error messages

### 🔧 Contributing Code

See sections below for detailed instructions!

---

## Development Setup

### Prerequisites

- **Python 3.11+**
- **Blender 5.0+**
- **Git**
- **Windows** (macOS/Linux support coming in v1.0)

### Initial Setup

1. **Fork and clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/frigg.git
   cd frigg
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .[dev]
   ```

4. **Verify installation:**
   ```bash
   python -m pytest
   .\tools\test_mcp_server.ps1
   ```

### Project Structure

```
D:\Frigg\
├── src/
│   └── frigg_mcp/
│       ├── __init__.py
│       └── server/
│           ├── __init__.py
│           └── stdio.py          # MCP server
├── tools/
│   ├── frigg-bridge.ps1          # Start Blender bridge
│   ├── frigg-stdio.ps1           # Start MCP server
│   ├── frigg_blender_bridge.py   # Blender bridge server
│   └── test_mcp_server.ps1       # Test suite
├── tests/                         # Test files
├── docs/                          # Documentation
├── logs/                          # Log files (gitignored)
├── ROADMAP.md                     # Project roadmap
├── ARCHITECTURE.md                # Technical architecture
├── PRIORITIES.md                  # Current priorities
└── CONTRIBUTING.md                # This file
```

---

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/add-rotation-tool
# OR
git checkout -b fix/connection-timeout
# OR
git checkout -b docs/improve-readme
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `test/` - Test improvements
- `refactor/` - Code refactoring

### 2. Make Your Changes

#### Adding a New Tool

**Example: Adding `set_rotation_euler` tool**

1. **Add tool to `tools_list()` in `stdio.py`:**
   ```python
   {
       "name": "frigg.blender.set_rotation_euler",
       "description": "Set object rotation in euler angles (degrees).",
       "inputSchema": {
           "type": "object",
           "properties": {
               "name": {"type": "string"},
               "rotation": {
                   "type": "array",
                   "items": {"type": "number"},
                   "minItems": 3,
                   "maxItems": 3
               }
           },
           "required": ["name", "rotation"],
           "additionalProperties": False,
       },
   }
   ```

2. **Add handler in `handle_call()` in `stdio.py`:**
   ```python
   if name == "frigg.blender.set_rotation_euler":
       args = arguments or {}
       response = call_bridge("set_rotation_euler", args)
       return response
   ```

3. **Add bridge function in `frigg_blender_bridge.py`:**
   ```python
   def set_rotation_euler(params):
       name = params.get("name")
       rotation = params.get("rotation")
       if not name or not isinstance(rotation, (list, tuple)) or len(rotation) != 3:
           raise ValueError("set_rotation_euler requires name and rotation[3]")

       obj = bpy.data.objects.get(name)
       if obj is None:
           raise ValueError(f"Object not found: {name}")

       # Convert degrees to radians
       import math
       rotation_rad = [math.radians(r) for r in rotation]
       obj.rotation_euler = rotation_rad

       return {
           "name": obj.name,
           "rotation_euler": [float(v) for v in obj.rotation_euler]
       }
   ```

4. **Add handler in bridge's `handle_request():`**
   ```python
   if method == "set_rotation_euler":
       return {"result": set_rotation_euler(params)}
   ```

5. **Write tests:**
   ```python
   # tests/test_rotation.py
   def test_set_rotation_euler():
       result = call_tool("frigg.blender.set_rotation_euler", {
           "name": "Cube",
           "rotation": [0, 0, 45]
       })
       assert result["name"] == "Cube"
       # Check rotation approximately equals 45° in radians
       assert abs(result["rotation_euler"][2] - 0.785) < 0.01
   ```

6. **Update documentation:**
   - Add to README.md tools list
   - Add example usage
   - Update TEST_RESULTS.md

### 3. Test Your Changes

```bash
# Run unit tests
pytest tests/

# Run full test suite
.\tools\test_mcp_server.ps1

# Test manually
cd D:\Frigg
.\tools\frigg-bridge.ps1 -UI
# In another terminal:
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"frigg.blender.set_rotation_euler","arguments":{"name":"Cube","rotation":[0,0,45]}}}' | .venv\Scripts\python.exe -m frigg_mcp.server.stdio
```

### 4. Format & Lint

```bash
# Format code
black src/ tools/

# Type check
mypy src/

# Lint
ruff check src/
```

---

## Submitting Changes

### 1. Commit Your Changes

**Write good commit messages:**

```bash
# Good commit message format:
git commit -m "feat(rotation): add set_rotation_euler tool

- Add MCP tool definition
- Implement bridge handler
- Convert degrees to radians
- Add tests with 95% coverage
- Update documentation

Closes #42"
```

**Commit message format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `test` - Tests
- `refactor` - Code refactoring
- `perf` - Performance improvement
- `chore` - Maintenance

**Examples:**
```bash
feat(materials): add material creation tools
fix(bridge): handle connection timeout gracefully
docs(readme): add installation instructions
test(rotation): add comprehensive rotation tests
refactor(stdio): simplify error handling
```

### 2. Push to Your Fork

```bash
git push origin feature/add-rotation-tool
```

### 3. Create Pull Request

1. Go to https://github.com/yourorg/frigg
2. Click "New Pull Request"
3. Select your branch
4. Fill out PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed

## Checklist
- [x] Code follows style guidelines
- [x] Self-review completed
- [x] Documentation updated
- [x] Tests added/updated
- [x] All tests pass

## Related Issues
Closes #42
Related to #38

## Screenshots (if applicable)
[Add screenshots of UI changes]
```

### 4. Code Review

- Maintainers will review your PR
- Address feedback promptly
- Make requested changes
- Push updates to same branch

### 5. Merge

Once approved:
- Maintainer will merge
- Your contribution will be in next release!
- You'll be added to CONTRIBUTORS.md

---

## Style Guidelines

### Python Style

**Follow PEP 8 with these specifics:**

```python
# Use type hints
def set_location(name: str, location: List[float]) -> Dict[str, Any]:
    pass

# Use descriptive variable names
object_name = params.get("name")  # Good
n = params.get("name")  # Bad

# Use docstrings for public functions
def call_bridge(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the Blender bridge with a method and parameters.

    Args:
        method: The bridge method to call
        params: Parameters for the method

    Returns:
        Response from the bridge

    Raises:
        RuntimeError: If bridge connection fails
    """
    pass

# Error messages should be actionable
raise RuntimeError(
    f"Cannot connect to bridge at {host}:{port}. "
    "Make sure to run frigg-bridge.ps1 first."
)  # Good

raise RuntimeError("Connection failed")  # Bad

# Use f-strings for formatting
message = f"Object {name} not found"  # Good
message = "Object {} not found".format(name)  # Bad
message = "Object " + name + " not found"  # Bad
```

### Naming Conventions

```python
# Functions and variables: snake_case
def get_object_transform():
    object_name = "Cube"

# Classes: PascalCase
class BridgeClient:
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_PORT = 8765
MAX_RETRIES = 3

# Private: prefix with underscore
def _internal_helper():
    pass
```

### Code Organization

```python
# Imports order:
import json  # 1. Standard library
import os
import sys

import bpy  # 2. Third party

from frigg_mcp.server import stdio  # 3. Local

# Group related functionality
class ObjectManipulation:
    @staticmethod
    def set_location(...): pass

    @staticmethod
    def set_rotation(...): pass

    @staticmethod
    def set_scale(...): pass
```

---

## Testing Guidelines

### Test Organization

```
tests/
├── unit/
│   ├── test_protocol.py       # Protocol parsing
│   ├── test_error_handling.py # Error handling
│   └── test_utils.py          # Utility functions
├── integration/
│   ├── test_bridge.py         # Bridge communication
│   └── test_tools.py          # Tool execution
└── e2e/
    └── test_workflows.py      # Full workflows
```

### Writing Tests

```python
# test_rotation.py
import pytest
from frigg_mcp.test_utils import call_tool, start_bridge

@pytest.fixture(scope="module")
def bridge():
    """Start bridge for all tests in module"""
    bridge = start_bridge()
    yield bridge
    bridge.stop()

def test_set_rotation_euler_success(bridge):
    """Test setting rotation succeeds"""
    result = call_tool("frigg.blender.set_rotation_euler", {
        "name": "Cube",
        "rotation": [0, 0, 45]
    })

    assert result["name"] == "Cube"
    assert len(result["rotation_euler"]) == 3

def test_set_rotation_euler_invalid_object(bridge):
    """Test error for non-existent object"""
    with pytest.raises(RuntimeError, match="Object not found"):
        call_tool("frigg.blender.set_rotation_euler", {
            "name": "NonExistent",
            "rotation": [0, 0, 45]
        })

def test_set_rotation_euler_invalid_params(bridge):
    """Test error for invalid parameters"""
    with pytest.raises(ValueError):
        call_tool("frigg.blender.set_rotation_euler", {
            "name": "Cube",
            "rotation": [0, 0]  # Only 2 values
        })
```

### Test Coverage

- Aim for >95% coverage
- Test happy path
- Test error cases
- Test edge cases (empty strings, null, etc.)
- Test boundary conditions

---

## Questions?

- **Documentation:** Read [ROADMAP.md](./ROADMAP.md), [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Chat:** Join our Discord (link TBD)
- **Issues:** Create an issue on GitHub
- **Email:** frigg-mcp@example.com (TBD)

---

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page
- Special mentions for major contributions

---

**Thank you for contributing to Frigg! Together we'll build the best Blender MCP in the world! 🚀**
