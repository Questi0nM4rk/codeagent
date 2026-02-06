"""Task lifecycle management backed by SurrealDB.

Business logic for creating, retrieving, completing, and listing tasks.
Handles priority ordering, dependency filtering, and project scoping.
"""

from __future__ import annotations

from typing import Any

from codeagent.mcp.db.client import SurrealDBClient
from codeagent.mcp.models import ErrorCode
from codeagent.mcp.models.task import TaskCreate


class TaskService:
    """Task lifecycle management backed by SurrealDB.

    Args:
        db: SurrealDB client for persistence.
    """

    def __init__(self, db: SurrealDBClient) -> None:
        self._db = db

    async def create_task(self, create: TaskCreate) -> dict[str, Any]:
        """Create a new task.

        Args:
            create: The task creation data.

        Returns:
            The created record dict from SurrealDB.
        """
        data = create.model_dump()
        result = await self._db.create("task", data)
        if isinstance(result, list):
            if not result:
                msg = "db.create returned an empty list"
                raise RuntimeError(msg)
            result = result[0]
        return result

    async def get_next_task(self, project: str | None = None) -> dict[str, Any]:
        """Get highest priority pending task with no unresolved dependencies.

        Anti-scope-creep: returns ONE task only.

        **Dependency contract**: This method only returns tasks whose
        ``depends_on`` array is empty (length 0). Callers are responsible for
        clearing entries from ``depends_on`` as upstream dependencies resolve.
        This is an intentional simplification -- dependency resolution is the
        caller's concern, not the query's.

        Args:
            project: Optional project filter.

        Returns:
            The next task dict, or an error dict with code NOT_FOUND.
        """
        filters = ["status = 'pending'"]
        params: dict[str, Any] = {}
        if project:
            filters.append("project = $project")
            params["project"] = project

        where = " AND ".join(filters)
        # S608: where clause is built from fixed column names, not user input
        # Only tasks with empty depends_on are eligible; see docstring contract.
        result = await self._db.query(
            f"SELECT * FROM task WHERE {where}"  # noqa: S608
            " AND array::len(depends_on) = 0"
            " ORDER BY priority ASC, created_at ASC LIMIT 1",
            params,
        )
        if result and isinstance(result, list) and result[0].get("result"):
            tasks = result[0]["result"]
            if tasks:
                return tasks[0]
        return {"error": "No pending tasks found", "code": ErrorCode.NOT_FOUND}

    async def complete_task(
        self,
        task_id: str,
        resolved_by: str | None = None,
        summary: str | None = None,
    ) -> dict[str, Any]:
        """Mark task as done.

        Args:
            task_id: The human-readable task identifier.
            resolved_by: Optional memory/episode record ID that resolved this task.
            summary: Optional completion summary.

        Returns:
            The updated task dict, or an error dict with code NOT_FOUND.
        """
        set_clauses = ["status = $status", "updated_at = time::now()"]
        params: dict[str, Any] = {"task_id": task_id, "status": "done"}
        if resolved_by is not None:
            set_clauses.append("resolved_by = $resolved_by")
            params["resolved_by"] = resolved_by
        if summary is not None:
            set_clauses.append("summary = $summary")
            params["summary"] = summary
        sets = ", ".join(set_clauses)
        result = await self._db.query(
            f"UPDATE task SET {sets} WHERE task_id = $task_id",  # noqa: S608
            params,
        )
        if result and isinstance(result, list) and result[0].get("result"):
            records = result[0]["result"]
            if records:
                return records[0]
        return {"error": f"Task {task_id} not found", "code": ErrorCode.NOT_FOUND}

    async def list_tasks(
        self,
        project: str | None = None,
        status: str | None = None,
        task_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """List and filter tasks.

        Args:
            project: Optional project filter.
            status: Optional status filter.
            task_type: Optional task type filter ('task' or 'epic').

        Returns:
            List of task dicts matching the filters.
        """
        filters: list[str] = []
        params: dict[str, Any] = {}
        if project:
            filters.append("project = $project")
            params["project"] = project
        if status:
            filters.append("status = $status")
            params["status"] = status
        if task_type:
            filters.append("type = $type")
            params["type"] = task_type

        where = f" WHERE {' AND '.join(filters)}" if filters else ""
        # S608: where clause is built from fixed column names, not user input
        result = await self._db.query(
            f"SELECT * FROM task{where} ORDER BY priority ASC, created_at ASC",  # noqa: S608
            params,
        )
        if result and isinstance(result, list) and result[0].get("result"):
            return result[0]["result"]
        return []
