"""MCP tool handlers for memory operations.

Each tool validates inputs, delegates to the appropriate service,
and returns a dict response (or ErrorResponse dict on failure).
"""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from codeagent.mcp.models import (
    ErrorCode,
    ErrorResponse,
    MemoryCreate,
    MemoryType,
    MemoryUpdate,
)
from codeagent.mcp.services.memory_service import MemoryService
from codeagent.mcp.services.search_service import SearchService

# Service instances, set by init_memory_tools()
_memory_service: MemoryService | None = None
_search_service: SearchService | None = None


def init_memory_tools(memory_service: MemoryService, search_service: SearchService) -> None:
    """Initialize tool dependencies.

    Must be called before any tool function is invoked.

    Args:
        memory_service: Service handling memory CRUD and linking.
        search_service: Service handling hybrid search.
    """
    global _memory_service, _search_service
    _memory_service = memory_service
    _search_service = search_service


async def store(
    type: str,
    content: str,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    project: str | None = None,
    confidence: float = 1.0,
    source_task: str | None = None,
) -> dict[str, Any]:
    """Store a new memory with auto-embedding and auto-linking.

    Args:
        type: Memory type (knowledge, episode, decision, pattern, code_chunk).
        content: The main text content of the memory.
        title: Optional human-readable title.
        metadata: Optional type-specific metadata.
        tags: Optional freeform tags for filtering.
        project: Optional project name for scoping.
        confidence: Confidence score, 0.0-1.0. Defaults to 1.0.
        source_task: Optional reference to the originating task record ID.

    Returns:
        Dict with the created memory or an error response.
    """
    if _memory_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        create = MemoryCreate(
            type=MemoryType(type),
            content=content,
            title=title,
            metadata=metadata or {},
            tags=tags or [],
            project=project,
            confidence=confidence,
            source_task=source_task,
        )
    except (ValueError, ValidationError) as e:
        return ErrorResponse(error=str(e), code=ErrorCode.VALIDATION_ERROR).model_dump()
    try:
        return await _memory_service.store(create)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def search(
    query: str,
    type: str | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    max_results: int = 10,
    *,
    include_graph: bool = False,
) -> dict[str, Any]:
    """Hybrid search across memory types.

    Args:
        query: Search query string.
        type: Optional memory type filter.
        project: Optional project name filter.
        tags: Optional tag filters.
        max_results: Maximum number of results to return.
        include_graph: Whether to include graph neighborhood data.

    Returns:
        Dict with search results or an error response.
    """
    if _search_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _search_service.search(
            query=query,
            memory_type=type,
            project=project,
            tags=tags,
            max_results=max_results,
            include_graph=include_graph,
        )
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def read(
    id: str,
    depth: int = 1,
) -> dict[str, Any]:
    """Read a memory by ID with graph neighborhood.

    Args:
        id: SurrealDB record ID (e.g. "memory:abc123").
        depth: Graph traversal depth (clamped to max 3).

    Returns:
        Dict with the memory record or an error response.
    """
    if _memory_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _memory_service.read(id, depth=min(depth, 3))
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def update(
    id: str,
    content: str | None = None,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    confidence: float | None = None,
) -> dict[str, Any]:
    """Update a memory. Re-embeds if content changes.

    Args:
        id: SurrealDB record ID of the memory to update.
        content: New content text, if updating.
        title: New title, if updating.
        metadata: New metadata, if updating.
        tags: New tags, if updating.
        confidence: New confidence score, if updating.

    Returns:
        Dict with the updated memory or an error response.
    """
    if _memory_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        upd = MemoryUpdate(
            memory_id=id,
            content=content,
            title=title,
            metadata=metadata,
            tags=tags,
            confidence=confidence,
        )
        return await _memory_service.update(upd)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def delete(id: str) -> dict[str, Any]:
    """Delete a memory (preserved in changefeed).

    Args:
        id: SurrealDB record ID to delete.

    Returns:
        Dict with deletion status or an error response.
    """
    if _memory_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _memory_service.delete(id)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def link(
    from_id: str,
    to_id: str,
    reason: str = "",
    strength: float = 0.8,
) -> dict[str, Any]:
    """Create a graph edge between two memories.

    Args:
        from_id: Source memory record ID.
        to_id: Target memory record ID.
        reason: Human-readable reason for the link.
        strength: Link strength, 0.0-1.0.

    Returns:
        Dict with link status or an error response.
    """
    if _memory_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _memory_service.link(from_id, to_id, reason, strength)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def stats(
    project: str | None = None,
    type: str | None = None,
) -> dict[str, Any]:
    """Memory statistics by type and project.

    Args:
        project: Optional project name to filter stats.
        type: Optional memory type to filter stats.

    Returns:
        Dict with statistics or an error response.
    """
    if _memory_service is None:
        return ErrorResponse(
            error="Memory tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _memory_service.stats(project, type)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()
