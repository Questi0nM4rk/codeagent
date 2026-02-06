"""Unified CodeAgent MCP server.

Uses FastMCP for tool registration. Services are initialized at runtime
via run_server() and injected into tool modules via init_*_tools().
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from codeagent.mcp.tools import memory as memory_tools

app = FastMCP("codeagent")


# --- Memory tools (7 tools) ---
app.add_tool(memory_tools.store)
app.add_tool(memory_tools.search)
app.add_tool(memory_tools.read)
app.add_tool(memory_tools.update)
app.add_tool(memory_tools.delete)
app.add_tool(memory_tools.link)
app.add_tool(memory_tools.stats)

# Future tool domains:
# - codeagent.mcp.tools.reflection
# - codeagent.mcp.tools.codebase
# - codeagent.mcp.tools.backlog


@app.tool()
async def ping() -> dict[str, str]:
    """Health check tool."""
    return {"status": "ok", "server": "codeagent"}


async def run_server() -> None:
    """Run the MCP server with initialized services.

    Creates DB client, embedding service, memory service, and search
    service. Injects them into tool modules then starts stdio transport.
    """
    from codeagent.mcp.db.client import SurrealDBClient
    from codeagent.mcp.embeddings import EmbeddingCache, EmbeddingProvider
    from codeagent.mcp.services.embedding_service import EmbeddingService
    from codeagent.mcp.services.memory_service import MemoryService
    from codeagent.mcp.services.search_service import SearchService

    db = SurrealDBClient(
        url=os.getenv("SURREAL_URL", "ws://localhost:8000"),
        username=os.getenv("SURREAL_USER", "root"),
        password=os.getenv("SURREAL_PASS", "root"),  # noqa: S106 - Default dev creds
    )
    await db.connect()

    schema_path = Path(__file__).parent / "db" / "schema.surql"
    await db.initialize_schema(schema_path)

    provider = EmbeddingProvider()
    cache = EmbeddingCache()
    embedding_svc = EmbeddingService(provider, cache)
    memory_svc = MemoryService(db, embedding_svc)
    search_svc = SearchService(db, embedding_svc)

    memory_tools.init_memory_tools(memory_svc, search_svc)

    await app.run_stdio_async()

    await db.close()


def main() -> None:
    """Entry point for codeagent-mcp command."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
