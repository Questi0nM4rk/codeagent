"""Tests for task tool handlers.

Each tool function is tested for:
- Correct delegation to the underlying service
- Correct error handling (returns ErrorResponse on failure)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestInitTaskTools:
    """Tests for init_task_tools() setup."""

    def test_init_task_tools_sets_service(self) -> None:
        """init_task_tools should set the module-level _task_service global."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = object()
        task_mod.init_task_tools(mock_svc)

        assert task_mod._task_service is mock_svc


class TestCreateTask:
    """Tests for the create_task() tool function."""

    @pytest.mark.asyncio()
    async def test_create_task_calls_service(self) -> None:
        """create_task() should delegate to _task_service."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.create_task.return_value = {"id": "task:abc", "task_id": "CA-001"}

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.create_task(
                project="project:myproj",
                name="Build feature",
                task_id="CA-001",
                description="Build the feature",
                priority=2,
            )

        mock_svc.create_task.assert_awaited_once()
        call_arg = mock_svc.create_task.call_args[0][0]

        from codeagent.mcp.models import TaskCreate

        assert isinstance(call_arg, TaskCreate)
        assert call_arg.project == "project:myproj"
        assert call_arg.name == "Build feature"
        assert call_arg.task_id == "CA-001"
        assert call_arg.description == "Build the feature"
        assert call_arg.priority == 2
        assert result == {"id": "task:abc", "task_id": "CA-001"}

    @pytest.mark.asyncio()
    async def test_create_task_returns_error_on_exception(self) -> None:
        """create_task() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.create_task.side_effect = RuntimeError("DB down")

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.create_task(
                project="project:x",
                name="test",
                task_id="CA-001",
            )

        assert "error" in result
        assert "DB down" in result["error"]

    @pytest.mark.asyncio()
    async def test_create_task_returns_error_on_validation_failure(self) -> None:
        """create_task() should return ErrorResponse for invalid priority."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.create_task(
                project="project:x",
                name="test",
                task_id="CA-001",
                priority=99,  # Invalid: must be 1-5
            )

        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"
        mock_svc.create_task.assert_not_awaited()


class TestGetNextTask:
    """Tests for the get_next_task() tool function."""

    @pytest.mark.asyncio()
    async def test_get_next_task_calls_service(self) -> None:
        """get_next_task() should forward project to _task_service.get_next_task."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.get_next_task.return_value = {
            "task_id": "CA-001",
            "name": "First task",
        }

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.get_next_task(project="project:myproj")

        mock_svc.get_next_task.assert_awaited_once_with(project="project:myproj")
        assert result == {"task_id": "CA-001", "name": "First task"}

    @pytest.mark.asyncio()
    async def test_get_next_task_returns_error_on_exception(self) -> None:
        """get_next_task() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.get_next_task.side_effect = RuntimeError("Query failed")

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.get_next_task()

        assert "error" in result
        assert "Query failed" in result["error"]
        assert result["code"] == "DB_ERROR"

    @pytest.mark.asyncio()
    async def test_get_next_task_defaults_project_to_none(self) -> None:
        """get_next_task() without project should pass None."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.get_next_task.return_value = {"task_id": "CA-001"}

        with patch.object(task_mod, "_task_service", mock_svc):
            await task_mod.get_next_task()

        mock_svc.get_next_task.assert_awaited_once_with(project=None)


class TestCompleteTask:
    """Tests for the complete_task() tool function."""

    @pytest.mark.asyncio()
    async def test_complete_task_calls_service(self) -> None:
        """complete_task() should forward task_id and resolved_by to service."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.complete_task.return_value = {"task_id": "CA-001", "status": "done"}

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.complete_task(
                task_id="CA-001", resolved_by="memory:ep1", summary="Done"
            )

        mock_svc.complete_task.assert_awaited_once_with(
            "CA-001", resolved_by="memory:ep1", summary="Done"
        )
        assert result == {"task_id": "CA-001", "status": "done"}

    @pytest.mark.asyncio()
    async def test_complete_task_returns_error_on_exception(self) -> None:
        """complete_task() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.complete_task.side_effect = RuntimeError("Update failed")

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.complete_task(task_id="CA-001")

        assert "error" in result
        assert "Update failed" in result["error"]
        assert result["code"] == "DB_ERROR"


class TestListTasks:
    """Tests for the list_tasks() tool function."""

    @pytest.mark.asyncio()
    async def test_list_tasks_calls_service(self) -> None:
        """list_tasks() should forward filters to _task_service.list_tasks."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.list_tasks.return_value = [
            {"task_id": "CA-001"},
            {"task_id": "CA-002"},
        ]

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.list_tasks(
                project="project:myproj", status="pending", task_type="task"
            )

        mock_svc.list_tasks.assert_awaited_once_with(
            project="project:myproj", status="pending", task_type="task"
        )
        assert result == {
            "tasks": [{"task_id": "CA-001"}, {"task_id": "CA-002"}],
            "count": 2,
        }

    @pytest.mark.asyncio()
    async def test_list_tasks_returns_error_on_exception(self) -> None:
        """list_tasks() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.list_tasks.side_effect = RuntimeError("List failed")

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.list_tasks()

        assert "error" in result
        assert "List failed" in result["error"]
        assert result["code"] == "DB_ERROR"

    @pytest.mark.asyncio()
    async def test_list_tasks_wraps_result_in_dict(self) -> None:
        """list_tasks() should wrap the list result with count."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.list_tasks.return_value = [{"task_id": "CA-001"}]

        with patch.object(task_mod, "_task_service", mock_svc):
            result = await task_mod.list_tasks()

        assert "tasks" in result
        assert "count" in result
        assert result["count"] == 1

    @pytest.mark.asyncio()
    async def test_list_tasks_defaults_all_filters_to_none(self) -> None:
        """list_tasks() without args should pass None for all filters."""
        from codeagent.mcp.tools import task as task_mod

        mock_svc = AsyncMock()
        mock_svc.list_tasks.return_value = []

        with patch.object(task_mod, "_task_service", mock_svc):
            await task_mod.list_tasks()

        mock_svc.list_tasks.assert_awaited_once_with(
            project=None, status=None, task_type=None
        )
