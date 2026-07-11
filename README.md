# Astrea

Astrea (**A**strophysics nuclear **S**ynthesis and **T**heoretical **R**eaction **E**valuation **A**gent) is a standalone AI-for-science engine linking microscopic nuclear physics to macroscopic astrophysics.

## Project Overview

In nuclear astrophysics, minor uncertainties in microscopic nuclear properties—such as resonance energies, stellar reaction rates, or astrophysical $S$-factors—can trigger cascading impacts on cosmic events (core-collapse supernovae, X-ray bursts, $r$-process nucleosynthesis). Identifying which nuclear reaction unlocks a given astrophysical puzzle is often beyond a single researcher’s synthesis capacity.

*ASTREA* is a domain-specific multi-agent system for that bottleneck: planning, testable hypothesis generation, and cited literature synthesis for nuclear astrophysics.

This repository is **self-contained** (Python package `astrea`). Phase 1 MVP covers **planning → hypotheses → literature** only (no MESA/FLASH, no nuclear-data MCP yet).

## Agent tree

```
InitAgent (sequential)
  ├─ PlannerAgent
  └─ OrchestratorAgent
       ├─ HypothesesAgent
       └─ ResearchAgent   # Tavily + optional papers_search / paper_analysis MCP
```

## Setup

Requires Python ≥ 3.12. The repo ships a `uv.lock`, so [uv](https://docs.astral.sh/uv/) is the recommended workflow (faster, reproducible). The `pip` path is kept as a fallback.

### Option A — uv (recommended)

```bash
cd Astrea
uv sync --extra dev          # creates .venv and installs pinned deps
cp .env.example .env         # fill LLM__* and SERVICES__TAVILY_API_KEY
```

Run anything via `uv run python ...` (no need to activate the venv):

```bash
uv run python validate.py
uv run python run_web.py
uv run pytest tests/test_assembly.py -q
```

### Option B — pip (fallback)

```bash
cd Astrea
python3 -m venv .venv && source .venv/bin/activate   # use python3 if python is absent
pip install -e ".[dev]"
cp .env.example .env         # fill LLM__* and SERVICES__TAVILY_API_KEY
```

## Run

The commands below assume you've activated the venv (`source .venv/bin/activate`) or are using `uv run` (see Setup). Examples use the bare names; prefix with `uv run` if you skipped activation.

```bash
# Assembly check (no LLM calls)
python validate.py

# Web UI — port 8020, HITL off by default
python run_web.py
python run_web.py --hitl

# Unit tests
pytest tests/test_assembly.py -q
```

## Environment

| Variable | Required | Purpose |
|----------|----------|---------|
| `LLM__OPENAI_API_KEY` / provider keys | yes | LLM access |
| `LLM__MAIN_MODEL` | yes | Main chat model (LiteLLM id) |
| `SERVICES__TAVILY_API_KEY` | yes | Web search |
| `MCP__PAPERS_SEARCH_URL` | no | OpenAlex papers MCP |
| `MCP__PAPER_ANALYSIS_URL` | no | Paper RAG MCP |
| `HITL__ENABLED` | no | Default false via `run_web.py` |
| `ASTREA_WEB_PORT` | no | Default 8020 |

## Acceptance queries

1. 简述 r-process 主要候选天体环境及观测约束。
2. 列出影响 $^{12}$C(α,γ)$^{16}$O 反应率不确定性的关键实验与评价库。
3. 给出 2–3 个可验证假设：某金属贫瘠星丰度模式是否支持多站点核合成。

Expect: plan → hypotheses and/or literature summary → cited final report.

## Layout

| Path | Role |
|------|------|
| `astrea/agents/system.yaml` | Agent tree |
| `astrea/agents/prompts/templates.py` | Domain prompts |
| `astrea/assembly/` | YAML → ADK assembler |
| `astrea/tools/` | Tavily / papers MCP / task tracker |
| `astrea/web/` | FastAPI UI |
| `run_web.py` / `validate.py` | Entrypoints |

## Usage

### 1. Web UI (default entrypoint)

```bash
python run_web.py                 # headless, HITL off — MVP default
python run_web.py --hitl          # enable human-in-the-loop review
```

Then open <http://127.0.0.1:8020> in a browser. Send a nuclear-astrophysics
question in the chat box; events stream back as the planner → orchestrator →
(hypotheses / research) pipeline runs, ending with a cited final report.

- Port: `ASTREA_WEB_PORT` (default `8020`).
- Stop a run: the **Stop** button cancels the active task and clears session memory.
- HITL: with `--hitl`, review cards appear in the browser for plan/approval steps;
  the `/api/hitl-status` endpoint shows which session agents have a handler.
- Diagnostics: `GET /api/agents` (roster), `GET /api/roadmap` (current plan JSON),
  `GET /api/events` (recent event log), `GET /api/tz-document` (optional TZ docs).

### 2. Programmatic usage

```python
import asyncio
from astrea.main import create_manager

async def main():
    manager = await create_manager()
    answer = await manager.run("简述 r-process 主要候选天体环境及观测约束。")
    print(answer)
    await manager.close()

asyncio.run(main())
```

`AstreaManager` exposes `run(query, verbose=True)` and an async context via
`initialize()` / `close()`. Direct `python -m astrea.main` is interactive but
discouraged — prefer the web UI.

### 3. Assembly check (no LLM, no keys)

```bash
python validate.py
# expected: "Astrea config OK" + 5 agents + "build_system: OK"
```

### 4. Tests

```bash
pytest tests/test_assembly.py -q
```

### Example queries

1. 简述 r-process 主要候选天体环境及观测约束。
2. 列出影响 $^{12}$C(α,γ)$^{16}$O 反应率不确定性的关键实验与评价库。
3. 给出 2–3 个可验证假设：某金属贫瘠星丰度模式是否支持多站点核合成。

Expected flow: plan → hypotheses and/or literature summary → cited final report.

### Notes & limits (Phase 1)

- No MESA / FLASH / full reaction-network simulation — the planner routes such
  requests to a literature/data-gap step and flags JINA REACLIB / ENDF / EXFOR.
- `ResearchAgent` uses Tavily by default; `papers_search` / `paper_analysis`
  MCP tools are picked up automatically when `MCP__PAPERS_SEARCH_URL` /
  `MCP__PAPER_ANALYSIS_URL` are set.
- LiteLLM model id comes from `LLM__MAIN_MODEL`; provider keys from
  `LLM__OPENAI_API_KEY` (or the matching provider env var).
