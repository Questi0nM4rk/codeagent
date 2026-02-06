"""Service layer for the unified MCP server.

Re-exports all services for convenient access:

    from codeagent.mcp.services import EmbeddingService, MemoryService, SearchService
"""

from __future__ import annotations

from codeagent.mcp.services.embedding_service import EmbeddingService
from codeagent.mcp.services.memory_service import MemoryService
from codeagent.mcp.services.search_service import SearchService

__all__ = ["EmbeddingService", "MemoryService", "SearchService"]
