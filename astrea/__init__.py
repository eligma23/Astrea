"""
Astrea — nuclear astrophysics multi-agent research assistant.
"""

__version__ = "0.1.0"

__all__ = [
    "AstreaManager",
    "create_manager",
]


def __getattr__(name: str):
    if name in ("AstreaManager", "create_manager"):
        from astrea.main import AstreaManager, create_manager

        return {"AstreaManager": AstreaManager, "create_manager": create_manager}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
