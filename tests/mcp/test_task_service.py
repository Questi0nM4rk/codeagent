"""Tests for TaskService - business logic for task lifecycle management."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from codeagent.mcp.models.task import TaskCreate
from codeagent.mcp.services.task_service import TaskService


def _make_task_create(**overrides: object) -> TaskCreate:
    """Create a TaskCreate instance with defaults."""
    defaults: dict[str, object] = {
        "task_id": "CA-TASK-001",
        "project": "project:testproj",
        "name": "Implement feature X",
    }
    defaults.update(overrides)
    return TaskCreate(**defaults)  # type: ignore[arg-type]


def _make_service(
    db: AsyncMock | None = None,
) -> tuple[TaskService, AsyncMock]:
    """Create a TaskService with a mock DB dependency."""
    mock_db = db or AsyncMock()
    service = TaskService(db=mock_db)
    return service, mock_db


class TestTaskServiceCreateTask:
    """Tests for TaskService.create_task() method."""

    @pytest.mark.asyncio
    async def test_create_task_calls_db_create(self) -> None:
        """create_task() should call db.create with 'task' table and model data."""
        service, mock_db = _make_service()
        mock_db.create.return_value = [{"id": "task:abc", "task_id": "CA-TASK-001"}]

        create = _make_task_create()
        await service.create_task(create)

        mock_db.create.assert_called_once()
        call_args = mock_db.create.call_args[0]
        assert call_args[0] == "task"
        data = call_args[1]
        assert data["task_id"] == "CA-TASK-001"
        assert data["project"] == "project:testproj"
        assert data["name"] == "Implement feature X"

    @pytest.mark.asyncio
    async def test_create_task_returns_created_record(self) -> None:
        """create_task() should return the created record dict."""
        service, mock_db = _make_service()
        mock_db.create.return_value = [{"id": "task:abc", "task_id": "CA-TASK-001"}]

        create = _make_task_create()
        result = await service.create_task(create)

        assert result == {"id": "task:abc", "task_id": "CA-TASK-001"}

    @pytest.mark.asyncio
    async def test_create_task_handles_list_response(self) -> None:
        """create_task() should unwrap list response from db.create."""
        service, mock_db = _make_service()
        mock_db.create.return_value = [{"id": "task:xyz"}]

        create = _make_task_create()
        result = await service.create_task(create)

        assert result == {"id": "task:xyz"}

    @pytest.mark.asyncio
    async def test_create_task_handles_dict_response(self) -> None:
        """create_task() should handle when db.create returns a dict directly."""
        service, mock_db = _make_service()
        mock_db.create.return_value = {"id": "task:single"}

        create = _make_task_create()
        result = await service.create_task(create)

        assert result["id"] == "task:single"


class TestTaskServiceGetNextTask:
    """Tests for TaskService.get_next_task() method."""

    @pytest.mark.asyncio
    async def test_get_next_task_returns_highest_priority_pending(self) -> None:
        """get_next_task() should return the highest priority pending task."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [
            {
                "result": [
                    {"id": "task:a", "task_id": "CA-001", "priority": 1, "status": "pending"}
                ]
            }
        ]

        result = await service.get_next_task()

        assert result["task_id"] == "CA-001"
        assert result["priority"] == 1

    @pytest.mark.asyncio
    async def test_get_next_task_filters_by_project(self) -> None:
        """get_next_task() should filter by project when provided."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [
            {"result": [{"id": "task:a", "task_id": "CA-001", "project": "project:myproj"}]}
        ]

        await service.get_next_task(project="project:myproj")

        query_call = mock_db.query.call_args
        query_str = query_call[0][0]
        assert "project = $project" in query_str
        assert query_call[0][1]["project"] == "project:myproj"

    @pytest.mark.asyncio
    async def test_get_next_task_returns_not_found_when_empty(self) -> None:
        """get_next_task() should return NOT_FOUND error when no pending tasks."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": []}]

        result = await service.get_next_task()

        assert result["error"] == "No pending tasks found"
        assert result["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_next_task_queries_pending_with_no_deps(self) -> None:
        """get_next_task() should only query pending tasks with empty depends_on."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": [{"id": "task:a"}]}]

        await service.get_next_task()

        query_str = mock_db.query.call_args[0][0]
        assert "status = 'pending'" in query_str
        assert "array::len(depends_on) = 0" in query_str
        assert "ORDER BY priority ASC" in query_str
        assert "LIMIT 1" in query_str


class TestTaskServiceCompleteTask:
    """Tests for TaskService.complete_task() method."""

    @pytest.mark.asyncio
    async def test_complete_task_updates_status_to_done(self) -> None:
        """complete_task() should update task status to 'done'."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [
            {"result": [{"id": "task:abc", "task_id": "CA-001", "status": "done"}]}
        ]

        result = await service.complete_task("CA-001")

        query_call = mock_db.query.call_args
        assert query_call[0][1]["status"] == "done"
        assert query_call[0][1]["task_id"] == "CA-001"
        assert result["status"] == "done"

    @pytest.mark.asyncio
    async def test_complete_task_includes_resolved_by(self) -> None:
        """complete_task() should include resolved_by when provided."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [
            {
                "result": [
                    {
                        "id": "task:abc",
                        "task_id": "CA-001",
                        "status": "done",
                        "resolved_by": "memory:ep1",
                    }
                ]
            }
        ]

        await service.complete_task("CA-001", resolved_by="memory:ep1")

        query_call = mock_db.query.call_args
        assert query_call[0][1]["resolved_by"] == "memory:ep1"

    @pytest.mark.asyncio
    async def test_complete_task_returns_not_found_for_missing(self) -> None:
        """complete_task() should return NOT_FOUND for a non-existent task."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": []}]

        result = await service.complete_task("CA-NONEXIST")

        assert result["error"] == "Task CA-NONEXIST not found"
        assert result["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_complete_task_returns_updated_record(self) -> None:
        """complete_task() should return the updated task record."""
        service, mock_db = _make_service()
        expected = {"id": "task:abc", "task_id": "CA-001", "status": "done"}
        mock_db.query.return_value = [{"result": [expected]}]

        result = await service.complete_task("CA-001")

        assert result == expected


class TestTaskServiceListTasks:
    """Tests for TaskService.list_tasks() method."""

    @pytest.mark.asyncio
    async def test_list_tasks_returns_all_tasks(self) -> None:
        """list_tasks() should return all tasks when no filters given."""
        service, mock_db = _make_service()
        tasks = [
            {"id": "task:a", "task_id": "CA-001"},
            {"id": "task:b", "task_id": "CA-002"},
        ]
        mock_db.query.return_value = [{"result": tasks}]

        result = await service.list_tasks()

        assert len(result) == 2
        assert result[0]["task_id"] == "CA-001"

    @pytest.mark.asyncio
    async def test_list_tasks_filters_by_project(self) -> None:
        """list_tasks() should filter by project when provided."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": [{"id": "task:a"}]}]

        await service.list_tasks(project="project:myproj")

        query_str = mock_db.query.call_args[0][0]
        assert "project = $project" in query_str
        assert mock_db.query.call_args[0][1]["project"] == "project:myproj"

    @pytest.mark.asyncio
    async def test_list_tasks_filters_by_status(self) -> None:
        """list_tasks() should filter by status when provided."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": []}]

        await service.list_tasks(status="done")

        query_str = mock_db.query.call_args[0][0]
        assert "status = $status" in query_str
        assert mock_db.query.call_args[0][1]["status"] == "done"

    @pytest.mark.asyncio
    async def test_list_tasks_filters_by_type(self) -> None:
        """list_tasks() should filter by task type when provided."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": []}]

        await service.list_tasks(task_type="epic")

        query_str = mock_db.query.call_args[0][0]
        assert "type = $type" in query_str
        assert mock_db.query.call_args[0][1]["type"] == "epic"

    @pytest.mark.asyncio
    async def test_list_tasks_returns_empty_list_when_no_results(self) -> None:
        """list_tasks() should return [] when no tasks match."""
        service, mock_db = _make_service()
        mock_db.query.return_value = [{"result": []}]

        result = await service.list_tasks()

        assert result == []
