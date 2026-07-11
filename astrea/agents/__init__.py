"""Astrea agents — assembled lazily from astrea/agents/system.yaml.

Build is deferred so ``import astrea.agents.prompts.templates`` (from the
assembler) does not re-enter ``astrea.assembly`` mid-import.
"""
from __future__ import annotations

from typing import Any

__all__ = [
    "agent_system",
    "orchestrator_agent",
    "root_agent",
    "planner_agent",
    "research_agent",
    "hypotheses_agent",
]

_system = None


def _ensure_system():
    global _system
    if _system is None:
        from opik.integrations.adk import track_adk_agent_recursive

        from astrea.agents.llm_repair import install_json_repair
        from astrea.assembly import build_system
        from astrea.logging import multi_agent_tracer

        install_json_repair()
        _system = build_system()
        track_adk_agent_recursive(_system.root, multi_agent_tracer)
    return _system


def __getattr__(name: str) -> Any:
    system = _ensure_system()
    mapping = {
        "agent_system": system,
        "orchestrator_agent": system.root,
        "root_agent": system.root,
        "planner_agent": system.agents.get("PlannerAgent"),
        "hypotheses_agent": system.agents.get("HypothesesAgent"),
        "research_agent": system.agents.get("ResearchAgent"),
    }
    if name in mapping:
        return mapping[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
