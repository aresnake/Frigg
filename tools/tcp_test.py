#!/usr/bin/env python
"""
TCP CLI helper (NOT a pytest test).

Usage:
  python tools/tcp_test.py <method> <code>

Example:
  python tools/tcp_test.py ping 200
"""

from __future__ import annotations

import sys


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python tools/tcp_test.py <method> <code>")
        return 2

    method = argv[1]
    code = argv[2]

    # NOTE: keep this as a minimal placeholder; implement real TCP call if/when needed.
    # This file must NEVER sys.exit() at import-time.
    print(f"[tcp_test] method={method} code={code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
