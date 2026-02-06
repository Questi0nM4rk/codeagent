"""Unified CodeAgent MCP server."""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

app = FastMCP("codeagent")


# Tool submodules: memory, reflection, codebase, backlog (Epic 6)


@app.tool()
async def ping() -> dict[str, str]:
    """Health check tool."""
    return {"status": "ok", "server": "codeagent"}


async def run_server() -> None:
    """Run the MCP server."""
    await app.run_stdio_async()


def main() -> None:
    """Entry point for codeagent-mcp command."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
