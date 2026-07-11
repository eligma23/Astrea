"""Launch the Astrea web UI (nuclear astrophysics Phase 1).

Usage (from the Astrea/ directory):
    python run_web.py          # headless (HITL off) — MVP default
    python run_web.py --hitl   # enable human review loops

Environment:
    ASTREA_WEB_PORT — port (default 8020)
    HITL__ENABLED   — same as --hitl / default false
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT))

# Load .env first so values like ASTREA_WEB_PORT / HITL__ENABLED / DEEPSEEK_API_KEY
# are in os.environ before defaults are applied or any astrea module is imported.
load_dotenv(_ROOT / ".env")

os.environ.setdefault("ASTREA_WEB_PORT", "8020")
if "--hitl" in sys.argv:
    os.environ["HITL__ENABLED"] = "true"
else:
    os.environ.setdefault("HITL__ENABLED", "false")

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "astrea.web.server:app",
        host="127.0.0.1",
        port=int(os.environ["ASTREA_WEB_PORT"]),
        reload=False,
        log_level="info",
    )
