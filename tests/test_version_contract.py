from __future__ import annotations

import frigg_mcp
from frigg_mcp.server import stdio


def test_runtime_version_matches_package_version():
    assert stdio.SERVER_INFO["version"] == frigg_mcp.__version__
