"""Embedding service for the unified MCP server."""

from __future__ import annotations

from codeagent.mcp.embeddings.cache import EmbeddingCache
from codeagent.mcp.embeddings.provider import EmbeddingProvider

__all__ = ["EmbeddingCache", "EmbeddingProvider"]
