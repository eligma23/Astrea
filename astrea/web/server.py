"""
Run the astrea web interface locally.

Usage:
    python -m astrea.web.server
    # or
    python astrea/web/server.py

Environment:
    ASTREA_CONFIG    — optional alternate YAML path; default agents/system.yaml
    ASTREA_WEB_PORT  — port to serve on (default 8000)
"""

import os
import sys
import uvicorn
from pathlib import Path

from dotenv import load_dotenv

root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

# Inject every var in .env into os.environ BEFORE any astrea module is imported.
# pydantic-settings only fills Settings fields from .env; third-party libs
# (e.g. litellm reads DEEPSEEK_API_KEY) need them in os.environ at call time.
load_dotenv(root_dir / ".env")

from astrea.web.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "astrea.web.server:app",
        host="127.0.0.1",
        port=int(os.environ.get("ASTREA_WEB_PORT", "8000")),
        reload=False,
        log_level="info",
    )
