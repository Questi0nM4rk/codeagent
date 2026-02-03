"""Unified CodeAgent MCP server."""

from __future__ import annotations

import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("codeagent")


# Tools will be registered here from submodules:
# - codeagent.mcp.tools.memory (A-MEM)
# - codeagent.mcp.tools.reflection
# - codeagent.mcp.tools.codebase
# - codeagent.mcp.tools.backlog


@app.tool()
async def ping() -> dict[str, str]:
    """Health check tool."""
    return {"status": "ok", "server": "codeagent"}


async def run_server() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main() -> None:
    """Entry point for codeagent-mcp command."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
