"""Registers tools, callbacks, agent classes and schemas for Astrea Phase 1.

Only nuclear-astrophysics MVP wiring: websearch, optional papers MCP,
task_tracker / create_plan, and Research/Planner callbacks.
"""
from __future__ import annotations

from astrea.assembly.registry import (
    REGISTRY,
    CallbackEntry,
    ToolDoc,
    ToolEntry,
)


def _websearch():
    from astrea.tools import websearch_toolset_instance
    return websearch_toolset_instance


def _paper_analysis():
    from astrea.tools import paper_analysis_toolset_instance
    return paper_analysis_toolset_instance


def _papers_search():
    from astrea.tools import papers_search_toolset_instance
    return papers_search_toolset_instance


def _task_tracker():
    from astrea.tools import task_tracker_instance
    return task_tracker_instance


def _create_plan_tool():
    from astrea.tools.task_tracker import create_plan_tool
    return [create_plan_tool()]


REGISTRY.register_tool(ToolEntry(
    key="websearch",
    factory=_websearch,
    runtime_resolved=True,
    docs=(
        ToolDoc(
            name="tavily_search",
            signature="tavily_search(query)",
            purpose="General web search.",
        ),
        ToolDoc(
            name="tavily_extract",
            signature="tavily_extract(urls)",
            purpose="Read the content of specific pages/URLs.",
        ),
        ToolDoc(
            name="tavily_crawl",
            signature="tavily_crawl(url)",
            purpose="Crawl a site starting from a URL when one page is not enough.",
        ),
    ),
))

REGISTRY.register_tool(ToolEntry(
    key="paper_analysis",
    factory=_paper_analysis,
    optional=True,
    runtime_resolved=True,
    docs=(
        ToolDoc(
            name="explore_my_papers",
            signature="explore_my_papers(question, s3_keys)",
            purpose="Answers questions using user-uploaded or previously downloaded papers.",
        ),
    ),
))

REGISTRY.register_tool(ToolEntry(
    key="papers_search",
    factory=_papers_search,
    optional=True,
    runtime_resolved=True,
    docs=(
        ToolDoc(
            name="search_papers",
            signature="search_papers(query, filters)",
            purpose=(
                "Searches scientific papers in OpenAlex using metadata and "
                "search filters. Does NOT download full paper files."
            ),
        ),
        ToolDoc(
            name="download_papers_from_search",
            signature="download_papers_from_search(query)",
            purpose="Searches and downloads papers for downstream analysis.",
        ),
    ),
))

REGISTRY.register_tool(ToolEntry(
    key="task_tracker",
    factory=_task_tracker,
    runtime_resolved=True,
    docs=(
        ToolDoc(
            name="get_active_tasks",
            signature="get_active_tasks(query)",
            purpose="Get tasks from TaskTracker",
        ),
        ToolDoc(
            name="update_task_status",
            signature="update_task_status(task_id)",
            purpose="Set task status to DONE/FAILED/IN_PROGRESS",
        ),
    ),
))

REGISTRY.register_tool(ToolEntry(
    key="create_plan_tool",
    factory=_create_plan_tool,
    docs=(
        ToolDoc(
            name="create_plan",
            signature="create_plan(tasks)",
            purpose="Replace all tasks with a new plan. Each task needs title, description, and assignee.",
        ),
    ),
))

HITL_TOOL_DOCS = (
    ToolDoc(
        name="request_approval",
        signature="request_approval(agent_name, message, context)",
        purpose=(
            "(HITL) Ask the human to approve or reject a proposed action before "
            "proceeding. Returns 'approved' (bool) and optional 'feedback'."
        ),
    ),
    ToolDoc(
        name="request_selection",
        signature="request_selection(agent_name, message, options)",
        purpose=(
            "(HITL) Ask the human to choose one of several options you generated "
            "(e.g. hypotheses or plans). Returns 'selected' and 'approved'."
        ),
    ),
)


def _cb(key: str, kind: str, func=None, factory=None) -> None:
    REGISTRY.register_callback(CallbackEntry(key=key, kind=kind, func=func, factory=factory))


def _inject_uploaded_papers():
    from astrea.agents.callbacks import papers_agent_before_model
    return papers_agent_before_model


def _log_research_tool_calls():
    from astrea.agents.callbacks import print_research_agent_tool_call
    return print_research_agent_tool_call


def _before_get_task():
    from astrea.agents.callbacks import before_get_task
    return before_get_task


def _web_search_limiter():
    from astrea.agents.callbacks.tool_callbacks import SearchLimiter
    return SearchLimiter(max_searches=2).limit_searches


_cb("inject_uploaded_papers", "before_model", factory=lambda ctx: _inject_uploaded_papers())
_cb("log_research_tool_calls", "after_tool", factory=lambda ctx: _log_research_tool_calls())
_cb("before_get_task", "before_agent", factory=lambda ctx: _before_get_task())
_cb("WebSearchLimiter", "before_tool", factory=lambda ctx: _web_search_limiter())


def _register_classes() -> None:
    from astrea.hitl.session_agent import SessionAgent

    REGISTRY.register_agent_class("session", SessionAgent)


def _register_schemas() -> None:
    from astrea.storage import MCPRanking, ToolRanking

    REGISTRY.register_output_schema("tool_ranking", ToolRanking)
    REGISTRY.register_output_schema("mcp_ranking", MCPRanking)


def _register_planners() -> None:
    from google.adk.planners import PlanReActPlanner

    REGISTRY.register_planner("plan_react", PlanReActPlanner)


_register_classes()
_register_schemas()
_register_planners()
