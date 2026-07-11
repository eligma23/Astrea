"""Validate the Astrea agent system builds without LLM calls.

Usage (from the Astrea/ directory):
    python validate.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("HITL__ENABLED", "false")

from astrea.assembly import build_system, load_config  # noqa: E402
from astrea.assembly.schema import resolve_config_path  # noqa: E402


def main() -> int:
    path = resolve_config_path()
    if not path.exists():
        print(f"ERROR: config not found: {path}", file=sys.stderr)
        return 1

    config = load_config(path)
    system = build_system(config)
    names = sorted(config.agents)
    print(f"Astrea config OK: {path}")
    print(f"  root: {config.root.name}")
    print(f"  agents ({len(names)}): {', '.join(names)}")
    for name in names:
        assert system.agent(name).name == name
    print("  build_system: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
