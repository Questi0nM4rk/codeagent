"""Tests for the unified CodeAgent MCP server.

Tests server registration, tool availability, and entry points.
"""

from __future__ import annotations


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
