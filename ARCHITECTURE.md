# Frigg MCP - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Claude Desktop                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Claude AI (LLM)                         │ │
│  │  - Interprets user requests                                │ │
│  │  - Generates MCP tool calls                                │ │
│  │  - Processes responses                                     │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │ MCP Protocol (JSON-RPC 2.0)          │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Frigg MCP Server (Python)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  stdio.py - MCP Protocol Handler                          │ │
│  │  - Request parsing & validation                           │ │
│  │  - Tool routing                                            │ │
│  │  - Error handling & logging                               │ │
│  │  - Response formatting                                     │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │ TCP Socket (JSON Line Protocol)      │
│  ┌───────────────────────▼────────────────────────────────────┐ │
│  │  Bridge Client                                             │ │
│  │  - Connection management                                   │ │
│  │  - Retry logic                                             │ │
│  │  - Timeout handling                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│              Blender + Bridge Server (Python)                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  frigg_blender_bridge.py - TCP Server                     │ │
│  │  - Socket listener (port 8765)                            │ │
│  │  - Request routing                                         │ │
│  │  - Thread safety                                           │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │                                       │
│  ┌───────────────────────▼────────────────────────────────────┐ │
│  │  Blender Python API (bpy)                                 │ │
│  │  - Scene manipulation                                      │ │
│  │  - Object operations                                       │ │
│  │  - Rendering                                               │ │
│  │  - Asset management                                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Blender UI                                                │ │
│  │  - Visual feedback                                         │ │
│  │  - Manual editing                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Component Deep Dive

### 1. MCP Server (stdio.py)

**Responsibilities:**
- Implement MCP protocol over stdio
- Parse and validate JSON-RPC 2.0 messages
- Route tool calls to appropriate handlers
- Manage bridge connection lifecycle
- Comprehensive error handling
- Logging and diagnostics

**Key Design Decisions:**

#### Protocol Compliance
```python
# Proper notification handling (no response for id=null)
if req_id is None:
    if method == "initialized":
        return None  # Don't respond to notifications
    # ...
```

#### Robust Error Handling
```python
# Multiple layers of error handling:
# 1. Connection errors (ConnectionRefusedError, timeout)
# 2. Bridge errors ({"error": "..."} in response)
# 3. Python exceptions (with full traceback logging)
# 4. Graceful shutdown (SIGTERM, SIGINT)
```

#### Retry Logic
```python
# Automatic retry for bridge_ping (bridge might be starting)
if method == "bridge_ping" and retry < 2:
    time.sleep(1)
    return call_bridge(method, params, retry + 1)
```

**Future Enhancements:**
- Connection pooling (reuse TCP connections)
- Request batching (send multiple operations at once)
- Async/await for concurrent operations
- Rate limiting per client
- Request queueing for long operations

### 2. Blender Bridge (frigg_blender_bridge.py)

**Responsibilities:**
- Run TCP server inside Blender
- Accept connections from MCP server
- Execute Blender operations safely
- Return results or errors
- Keep Blender responsive (threading)

**Key Design Decisions:**

#### Thread Safety
```python
# Accept loop runs in separate thread to avoid blocking Blender
thread = threading.Thread(target=_accept_loop, args=(server,), daemon=True)
thread.start()

# Keepalive timer ensures thread keeps running
bpy.app.timers.register(_keepalive, first_interval=0.5, persistent=True)
```

#### Request-Response Protocol
```
Client → Server: {"method": "get_object_transform", "params": {"name": "Cube"}}\n
Server → Client: {"result": {"name": "Cube", "location": [0,0,0], ...}}\n
```

**Future Enhancements:**
- Connection authentication (token-based)
- Multi-client support (multiple Claude instances)
- Operation queuing (handle multiple requests)
- Progress reporting for long operations
- Undo/redo stack integration

### 3. Tool Architecture

**Current Tools (v0.4):**

```python
TOOLS = {
    "frigg.ping": NoBlenderRequired,
    "frigg.blender.bridge_ping": BlenderConnection,
    "frigg.blender.scene_info": ReadOnly,
    "frigg.blender.list_objects": ReadOnly,
    "frigg.blender.get_object_transform": ReadOnly,
    "frigg.blender.set_object_location": Mutating,
    "frigg.blender.move_object": Mutating,
}
```

**Tool Categories:**

1. **NoBlenderRequired** - MCP server only, no bridge
2. **ReadOnly** - Query Blender state, no modifications
3. **Mutating** - Change Blender state
4. **LongRunning** - Operations >5s (future)
5. **Batch** - Multiple operations (future)

**Tool Design Pattern:**

```python
# Each tool follows this pattern:
def tool_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    # 1. Validate parameters
    if not validate_params(params):
        raise ValueError("Invalid parameters")

    # 2. Execute operation
    result = perform_blender_operation(params)

    # 3. Format response
    return {"result": result}
```

### 4. Error Handling Strategy

**Error Hierarchy:**

```
MCP Error (-32xxx JSON-RPC codes)
├── Parse Error (-32700)
├── Invalid Request (-32600)
├── Method Not Found (-32601)
├── Invalid Params (-32602)
└── Internal Error (-32603)
    ├── Bridge Connection Error
    │   ├── ConnectionRefusedError → "Bridge not running"
    │   ├── TimeoutError → "Bridge timeout"
    │   └── OSError → "Network error"
    ├── Bridge Execution Error
    │   ├── ValueError → "Invalid operation"
    │   ├── KeyError → "Object not found"
    │   └── RuntimeError → "Blender error"
    └── Unexpected Error
        └── Exception → "Internal error" + traceback
```

**Error Context:**

```python
# Always provide actionable error messages
raise RuntimeError(
    f"Cannot connect to Blender bridge at {host}:{port}. "
    "Make sure to run frigg-bridge.ps1 first to start Blender."
)
```

### 5. Logging Architecture

**Multi-Level Logging:**

```
Level 1: stderr (captured by Claude Desktop)
├── Startup messages
├── Error messages
└── Warnings

Level 2: File logs (D:\Frigg\logs\frigg_mcp_server.log)
├── All of Level 1
├── Stack traces
├── Debug information
└── Timestamped entries

Level 3: Claude Desktop logs (%APPDATA%\Claude\logs\mcp-server-frigg.log)
├── MCP protocol messages
├── Tool invocations
└── Connection lifecycle
```

**Log Rotation (Future):**
```python
# Implement log rotation to prevent unbounded growth
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler(
    'logs/frigg_mcp_server.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### 6. Configuration Management

**Configuration Sources (Priority Order):**

1. **Environment Variables** (highest priority)
   - `FRIGG_BRIDGE_HOST`
   - `FRIGG_BRIDGE_PORT`
   - `BLENDER_EXE`

2. **State File** (.frigg_bridge.json)
   ```json
   {
     "host": "127.0.0.1",
     "port": 8765,
     "pid": 12345,
     "started_at_iso": "2026-01-11T12:00:00Z"
   }
   ```

3. **Defaults**
   - Host: 127.0.0.1
   - Port: 8765
   - Blender: Auto-detect

**Future: Config File (frigg.toml):**
```toml
[server]
host = "127.0.0.1"
port = 8765
timeout = 30
retry_attempts = 3

[logging]
level = "INFO"
file = "logs/frigg_mcp_server.log"
max_size = "10MB"
backup_count = 5

[blender]
executable = "C:\\Program Files\\Blender Foundation\\Blender 5.0\\blender.exe"
headless = false
```

### 7. Testing Strategy

**Test Pyramid:**

```
                    ┌─────────────┐
                    │   E2E Tests │ (10%)
                    │  - Full MCP │
                    │  - Blender  │
                    └─────────────┘
                  ┌─────────────────┐
                  │ Integration Tests│ (30%)
                  │  - Bridge comms  │
                  │  - Tool execution│
                  └─────────────────┘
              ┌───────────────────────┐
              │     Unit Tests        │ (60%)
              │  - Request parsing    │
              │  - Error handling     │
              │  - Utility functions  │
              └───────────────────────┘
```

**Test Categories:**

1. **Unit Tests** (pytest)
   - Protocol parsing
   - Error handling
   - Utility functions
   - Mock bridge responses

2. **Integration Tests**
   - Real bridge connection
   - Tool execution
   - Error scenarios
   - Performance tests

3. **E2E Tests**
   - Full MCP protocol
   - Claude Desktop simulation
   - Multi-step workflows
   - Error recovery

**Test Automation (Future):**
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Run tests
        run: pytest --cov=frigg_mcp
```

### 8. Performance Optimization

**Current Bottlenecks:**

1. **TCP Round Trip** (~1-5ms per tool call)
2. **JSON Serialization** (~0.1ms per call)
3. **Blender Operation** (varies: 0.1-100ms)

**Optimization Strategies:**

#### Batch Operations (v0.8+)
```python
# Instead of:
set_object_location("Cube", [1,0,0])
set_object_location("Sphere", [2,0,0])
set_object_location("Cone", [3,0,0])

# Use:
batch_set_locations([
    {"name": "Cube", "location": [1,0,0]},
    {"name": "Sphere", "location": [2,0,0]},
    {"name": "Cone", "location": [3,0,0]},
])
# Single TCP round trip instead of three
```

#### Connection Pool (v0.9+)
```python
# Keep TCP connection open between requests
class BridgeConnectionPool:
    def __init__(self, max_connections=5):
        self.pool = []
        self.max_connections = max_connections

    def get_connection(self):
        # Reuse existing connection or create new
        pass
```

#### Caching (v1.0+)
```python
# Cache read-only operations
@lru_cache(maxsize=128)
def get_object_transform(name: str):
    # Cache for 100ms to avoid redundant queries
    pass
```

**Performance Targets:**

- Tool call latency: <100ms (p95)
- Bridge connection: <50ms
- Batch operations: 10+ ops in <150ms
- Memory usage: <50MB (server + bridge)

### 9. Security Considerations

**Current Security Measures:**

1. **Local-only by default** (127.0.0.1 binding)
2. **No authentication** (trusted local environment)
3. **Input validation** (parameter type checking)
4. **Error sanitization** (no sensitive data in errors)

**Future Security (v1.0+):**

#### Authentication
```python
# Token-based authentication
def authenticate_request(token: str) -> bool:
    return secrets.compare_digest(token, EXPECTED_TOKEN)
```

#### Sandboxing Python Execution
```python
# Restricted Python execution for user scripts
import RestrictedPython

def execute_safe_script(script: str):
    compiled = RestrictedPython.compile_restricted(script)
    # Execute in restricted environment
```

#### Rate Limiting
```python
# Prevent abuse
@rate_limit(calls=100, period=60)  # 100 calls per minute
def tool_handler(params):
    pass
```

### 10. Extensibility & Plugins

**Plugin Architecture (v1.3+):**

```python
# plugins/my_plugin.py
from frigg_mcp import PluginBase, tool

class MyPlugin(PluginBase):
    name = "my_plugin"
    version = "1.0.0"

    @tool(
        name="my_plugin.custom_tool",
        description="Custom tool description",
        parameters={
            "param1": {"type": "string", "required": True}
        }
    )
    def custom_tool(self, params):
        return {"result": "custom result"}
```

**Plugin Discovery:**
```python
# Scan plugins directory
plugins = []
for file in Path("plugins").glob("*.py"):
    plugin = load_plugin(file)
    plugins.append(plugin)
```

### 11. Monitoring & Observability

**Metrics to Track (v1.0+):**

```python
from prometheus_client import Counter, Histogram

# Request metrics
requests_total = Counter('frigg_requests_total', 'Total requests', ['tool', 'status'])
request_duration = Histogram('frigg_request_duration_seconds', 'Request duration')

# Bridge metrics
bridge_connections = Counter('frigg_bridge_connections_total', 'Bridge connections')
bridge_errors = Counter('frigg_bridge_errors_total', 'Bridge errors', ['type'])
```

**Health Checks:**
```python
@app.route('/health')
def health():
    return {
        "status": "healthy" if bridge_alive() else "degraded",
        "bridge_connected": bridge_alive(),
        "uptime_seconds": get_uptime(),
        "version": "0.4.0"
    }
```

### 12. Deployment & Distribution

**Current Distribution:**

1. **Local development** (git clone + setup)
2. **Virtual environment** (.venv with requirements)
3. **Manual configuration** (Claude Desktop config)

**Future Distribution (v1.0+):**

#### PyPI Package
```bash
pip install frigg-mcp
frigg-mcp init  # Auto-configure Claude Desktop
```

#### Docker Container
```dockerfile
FROM python:3.11
RUN pip install frigg-mcp
CMD ["frigg-mcp", "serve"]
```

#### Installer (Windows)
```
FriggMCP-Setup-v1.0.0.exe
- Installs Python if needed
- Configures Claude Desktop automatically
- Adds to Start menu
```

---

## Technology Stack

### Core Technologies
- **Python 3.11+** - Main language
- **Blender 5.0+** - 3D software
- **MCP Protocol** - Communication standard
- **JSON-RPC 2.0** - Message format

### Dependencies
```toml
[dependencies]
# Production
typing-extensions = "^4.0"  # Type hints

[dev-dependencies]
# Development
pytest = "^7.0"              # Testing
pytest-cov = "^4.0"          # Coverage
black = "^23.0"              # Formatting
mypy = "^1.0"                # Type checking
ruff = "^0.1"                # Linting
```

### Future Dependencies
- **prometheus-client** - Metrics
- **RestrictedPython** - Sandboxing
- **aiohttp** - Async HTTP
- **pydantic** - Validation
- **structlog** - Structured logging

---

## Development Workflow

### Local Development
```bash
# Setup
cd D:\Frigg
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]

# Run tests
pytest

# Start Blender bridge
.\tools\frigg-bridge.ps1 -UI

# Test MCP server
.\tools\test_mcp_server.ps1
```

### Code Quality
```bash
# Format code
black src/ tools/

# Type check
mypy src/

# Lint
ruff check src/

# Run all checks
pre-commit run --all-files
```

### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Tag release: `git tag v0.x.x`
5. Push: `git push --tags`
6. CI builds and publishes

---

## Conclusion

Frigg MCP est conçu avec les principes suivants:

1. **Reliability** - Ça marche, tout le temps
2. **Performance** - Rapide et efficace
3. **Maintainability** - Code propre, bien structuré
4. **Extensibility** - Facile d'ajouter des fonctionnalités
5. **User-Friendly** - Expérience fluide pour utilisateurs et développeurs

Cette architecture nous permet d'atteindre notre objectif: **le meilleur MCP Blender au monde**.
