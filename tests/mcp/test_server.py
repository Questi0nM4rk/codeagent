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

    def test_all_tools_registered_on_app(self) -> None:
        """All expected tools should be registered on the FastMCP app."""
        from codeagent.mcp.server import app

        # FastMCP stores tools in _tool_manager._tools dict
        registered = app._tool_manager._tools
        expected = {
            "store",
            "search",
            "read",
            "update",
            "delete",
            "link",
            "stats",
            "create_task",
            "get_next_task",
            "complete_task",
            "list_tasks",
            "reflect",
            "improved_attempt",
            "model_effectiveness",
            "ping",
        }
        assert set(registered.keys()) == expected
