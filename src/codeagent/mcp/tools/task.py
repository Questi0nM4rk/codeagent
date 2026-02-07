"""MCP tool handlers for task operations.

Each tool validates inputs, delegates to the task service,
and returns a dict response (or ErrorResponse dict on failure).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import ValidationError

from codeagent.mcp.models import (
    ErrorCode,
    ErrorResponse,
    TaskCreate,
    TaskStatus,
    TaskType,
)

if TYPE_CHECKING:
    from codeagent.mcp.services.task_service import TaskService

# Service instance, set by init_task_tools()
_task_service: TaskService | None = None


def init_task_tools(task_service: TaskService) -> None:
    """Initialize tool dependencies.

    Must be called before any tool function is invoked.

    Args:
        task_service: Service handling task lifecycle operations.
    """
    global _task_service  # noqa: PLW0603
    _task_service = task_service


async def create_task(  # noqa: PLR0913
    project: str,
    name: str,
    task_id: str,
    task_type: str = "task",
    description: str | None = None,
    status: str = "pending",
    priority: int = 3,
    files_exclusive: list[str] | None = None,
    files_readonly: list[str] | None = None,
    depends_on: list[str] | None = None,
    parent: str | None = None,
    suggested_model: str | None = None,
) -> dict[str, Any]:
    """Create a new task in the backlog.

    Args:
        project: SurrealDB record ID of the parent project.
        name: Short name describing the task.
        task_id: Human-readable task identifier (e.g. "CA-TASK-001").
        task_type: Task type - 'task' or 'epic'.
        description: Optional longer description.
        status: Initial task status.
        priority: Priority 1 (highest) to 5 (lowest).
        files_exclusive: Files only this task may modify.
        files_readonly: Files this task may read but not modify.
        depends_on: List of task record IDs this depends on.
        parent: Optional parent task record ID.
        suggested_model: Optional model suggestion (e.g. "haiku", "opus").

    Returns:
        Dict with the created task or an error response.
    """
    if _task_service is None:
        return ErrorResponse(
            error="Task tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        create = TaskCreate(
            task_id=task_id,
            project=project,
            name=name,
            type=TaskType(task_type),
            description=description,
            status=TaskStatus(status),
            priority=priority,
            files_exclusive=files_exclusive or [],
            files_readonly=files_readonly or [],
            depends_on=depends_on or [],
            parent=parent,
            suggested_model=suggested_model,
        )
    except (ValueError, ValidationError) as e:
        return ErrorResponse(error=str(e), code=ErrorCode.VALIDATION_ERROR).model_dump()
    try:
        return await _task_service.create_task(create)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def get_next_task(
    project: str | None = None,
) -> dict[str, Any]:
    """Get the highest priority pending task with no unresolved dependencies.

    Args:
        project: Optional project filter.

    Returns:
        Dict with the next task or an error response.
    """
    if _task_service is None:
        return ErrorResponse(
            error="Task tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _task_service.get_next_task(project=project)
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def complete_task(
    task_id: str,
    resolved_by: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    """Mark a task as done.

    Args:
        task_id: The human-readable task identifier.
        resolved_by: Optional memory/episode record ID that resolved this task.
        summary: Optional completion summary.

    Returns:
        Dict with the updated task or an error response.
    """
    if _task_service is None:
        return ErrorResponse(
            error="Task tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        return await _task_service.complete_task(
            task_id,
            resolved_by=resolved_by,
            summary=summary,
        )
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def list_tasks(
    project: str | None = None,
    status: str | None = None,
    task_type: str | None = None,
) -> dict[str, Any]:
    """List and filter tasks from the backlog.

    Args:
        project: Optional project filter.
        status: Optional status filter.
        task_type: Optional task type filter ('task' or 'epic').

    Returns:
        Dict with tasks list and count, or an error response.
    """
    if _task_service is None:
        return ErrorResponse(
            error="Task tools not initialized", code=ErrorCode.VALIDATION_ERROR
        ).model_dump()
    try:
        tasks = await _task_service.list_tasks(
            project=project,
            status=status,
            task_type=task_type,
        )
        return {"tasks": tasks, "count": len(tasks)}
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()
