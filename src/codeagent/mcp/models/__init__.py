"""Pydantic models for the unified CodeAgent MCP server.

Re-exports all models from submodules for convenient access:

    from codeagent.mcp.models import Memory, MemoryCreate, Task, ErrorResponse
"""

from __future__ import annotations

from codeagent.mcp.models.common import ErrorCode, ErrorResponse
from codeagent.mcp.models.memory import (
    Memory,
    MemoryCreate,
    MemoryType,
    MemoryUpdate,
    SearchResponse,
    SearchResult,
)
from codeagent.mcp.models.task import (
    Project,
    Task,
    TaskCreate,
    TaskStatus,
    TaskType,
)

__all__ = [
    # Common
    "ErrorCode",
    "ErrorResponse",
    # Memory
    "Memory",
    "MemoryCreate",
    "MemoryType",
    "MemoryUpdate",
    "SearchResponse",
    "SearchResult",
    # Task
    "Project",
    "Task",
    "TaskCreate",
    "TaskStatus",
    "TaskType",
]
