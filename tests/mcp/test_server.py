"""Tests for the unified CodeAgent MCP server.

Tests server registration, tool availability, and entry points.
"""

from __future__ import annotations

import pytest


class TestServerApp:
    """Tests for the MCP server app instance."""

    def test_server_app_exists(self) -> None:
        """The server module should export an 'app' that is a FastMCP instance."""
        from mcp.server.fastmcp import FastMCP

        from codeagent.mcp.server import app

        assert isinstance(app, FastMCP)

    def test_server_name(self) -> None:
        """The server app name should be 'codeagent'."""
        from codeagent.mcp.server import app

        assert app.name == "codeagent"

    def test_main_entry_point_exists(self) -> None:
        """The server module should define a main() callable."""
        from codeagent.mcp.server import main

        assert callable(main)

    def test_run_server_exists(self) -> None:
        """The server module should define an async run_server() callable."""
        import asyncio

        from codeagent.mcp.server import run_server

        assert callable(run_server)
        assert asyncio.iscoroutinefunction(run_server)

    def test_server_has_ping_tool(self) -> None:
        """The server should have a 'ping' tool registered."""
        from codeagent.mcp.server import ping

        assert callable(ping)


class TestToolImports:
    """Verify all 14 tool functions are importable from their respective modules."""

    # -- Memory tools (7) --

    @pytest.mark.parametrize(
        "tool_name",
        ["store", "search", "read", "update", "delete", "link", "stats"],
    )
    def test_memory_tool_importable(self, tool_name: str) -> None:
        """Each memory tool function should be importable and callable."""
        from codeagent.mcp.tools import memory as mem_mod

        tool_fn = getattr(mem_mod, tool_name)
        assert callable(tool_fn)

    # -- Task tools (4) --

    @pytest.mark.parametrize(
        "tool_name",
        ["create_task", "get_next_task", "complete_task", "list_tasks"],
    )
    def test_task_tool_importable(self, tool_name: str) -> None:
        """Each task tool function should be importable and callable."""
        from codeagent.mcp.tools import task as task_mod

        tool_fn = getattr(task_mod, tool_name)
        assert callable(tool_fn)

    # -- Reflection tools (3) --

    @pytest.mark.parametrize(
        "tool_name",
        ["reflect", "improved_attempt", "model_effectiveness"],
    )
    def test_reflection_tool_importable(self, tool_name: str) -> None:
        """Each reflection tool function should be importable and callable."""
        from codeagent.mcp.tools import reflect as ref_mod

        tool_fn = getattr(ref_mod, tool_name)
        assert callable(tool_fn)

    def test_all_14_tools_accounted_for(self) -> None:
        """There should be exactly 14 tool functions across the three tool modules."""
        from codeagent.mcp.tools import memory as mem_mod
        from codeagent.mcp.tools import reflect as ref_mod
        from codeagent.mcp.tools import task as task_mod

        memory_tools = ["store", "search", "read", "update", "delete", "link", "stats"]
        task_tools = ["create_task", "get_next_task", "complete_task", "list_tasks"]
        reflection_tools = ["reflect", "improved_attempt", "model_effectiveness"]

        all_tools: list[tuple[object, str]] = [
            *[(mem_mod, t) for t in memory_tools],
            *[(task_mod, t) for t in task_tools],
            *[(ref_mod, t) for t in reflection_tools],
        ]

        assert len(all_tools) == 14
        for mod, name in all_tools:
            assert callable(getattr(mod, name)), f"{mod.__name__}.{name} not callable"
