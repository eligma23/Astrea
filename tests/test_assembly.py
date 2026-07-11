"""Structural tests for Astrea (astrea/agents/system.yaml).

Run from Astrea/:  pytest tests/test_assembly.py -q
"""
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
os.environ.setdefault("HITL__ENABLED", "false")

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from astrea.assembly import build_system, load_config
from astrea.assembly.schema import resolve_config_path


@pytest.fixture(scope="module")
def config():
    return load_config(resolve_config_path())


@pytest.fixture(scope="module")
def system(config):
    return build_system(config)


def test_default_config_is_system_yaml():
    path = resolve_config_path()
    assert path.name == "system.yaml" and path.exists()


def test_root_pipeline(config):
    assert config.root.name == "InitAgent"
    assert config.root.children == ["PlannerAgent", "OrchestratorAgent"]


def test_only_phase1_agents(config):
    assert set(config.agents) == {
        "InitAgent",
        "PlannerAgent",
        "OrchestratorAgent",
        "HypothesesAgent",
        "ResearchAgent",
    }
    assert config.agent("OrchestratorAgent").subordinates == [
        "HypothesesAgent",
        "ResearchAgent",
    ]


def test_system_builds(config, system):
    for name in config.agents:
        assert system.agent(name).name == name


def test_planner_prompt(system):
    instruction = system.agent("PlannerAgent").instruction
    assert "create_plan" in instruction
    assert "HypothesesAgent" in instruction
    assert "ResearchAgent" in instruction
    for absent in ("TaskExecutorAgent", "CoderAgent", "MedicalAgent", "retrieve_tools"):
        assert absent not in instruction


def test_orchestrator_prompt(system):
    instruction = system.agent("OrchestratorAgent").instruction
    assert "{active_tasks}" in instruction
    assert "HypothesesAgent" in instruction
    assert "ResearchAgent" in instruction


def test_hypotheses_prompt(system):
    instruction = system.agent("HypothesesAgent").instruction
    assert "testable" in instruction.lower()


def test_research_prompt(system):
    instruction = system.agent("ResearchAgent").instruction
    assert "Sources" in instruction or "citation" in instruction.lower()


def test_no_unfilled_placeholders(config, system):
    for name in config.agents:
        instruction = getattr(system.agent(name), "instruction", "") or ""
        assert "<<" not in instruction, f"{name}: unfilled placeholder"


def test_no_coscientist_imports():
    """Astrea must not import the parent CoScientist package."""
    root = _ROOT / "astrea"
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "CoScientist" not in text, f"{path} still references CoScientist"
        assert "from coscientist" not in text.lower()
