"""Tests for models package exports."""

from __future__ import annotations


class TestModelsExports:
    """Verify that all models are exported from the models package."""

    def test_exports_memory_type(self) -> None:
        """Package should export MemoryType."""
        from codeagent.mcp.models import MemoryType

        assert MemoryType.KNOWLEDGE == "knowledge"

    def test_exports_memory(self) -> None:
        """Package should re-export Memory with correct identity."""
        from codeagent.mcp.models import Memory
        from codeagent.mcp.models.memory import Memory as OrigMemory

        assert Memory is OrigMemory

    def test_exports_memory_create(self) -> None:
        """Package should re-export MemoryCreate with correct identity."""
        from codeagent.mcp.models import MemoryCreate
        from codeagent.mcp.models.memory import MemoryCreate as OrigMemoryCreate

        assert MemoryCreate is OrigMemoryCreate

    def test_exports_memory_update(self) -> None:
        """Package should re-export MemoryUpdate with correct identity."""
        from codeagent.mcp.models import MemoryUpdate
        from codeagent.mcp.models.memory import MemoryUpdate as OrigMemoryUpdate

        assert MemoryUpdate is OrigMemoryUpdate

    def test_exports_search_result(self) -> None:
        """Package should re-export SearchResult with correct identity."""
        from codeagent.mcp.models import SearchResult
        from codeagent.mcp.models.memory import SearchResult as OrigSearchResult

        assert SearchResult is OrigSearchResult

    def test_exports_search_response(self) -> None:
        """Package should re-export SearchResponse with correct identity."""
        from codeagent.mcp.models import SearchResponse
        from codeagent.mcp.models.memory import SearchResponse as OrigSearchResponse

        assert SearchResponse is OrigSearchResponse

    def test_exports_task_status(self) -> None:
        """Package should export TaskStatus."""
        from codeagent.mcp.models import TaskStatus

        assert TaskStatus.PENDING == "pending"

    def test_exports_task_type(self) -> None:
        """Package should export TaskType."""
        from codeagent.mcp.models import TaskType

        assert TaskType.TASK == "task"

    def test_exports_task(self) -> None:
        """Package should re-export Task with correct identity."""
        from codeagent.mcp.models import Task
        from codeagent.mcp.models.task import Task as OrigTask

        assert Task is OrigTask

    def test_exports_task_create(self) -> None:
        """Package should re-export TaskCreate with correct identity."""
        from codeagent.mcp.models import TaskCreate
        from codeagent.mcp.models.task import TaskCreate as OrigTaskCreate

        assert TaskCreate is OrigTaskCreate

    def test_exports_project(self) -> None:
        """Package should re-export Project with correct identity."""
        from codeagent.mcp.models import Project
        from codeagent.mcp.models.task import Project as OrigProject

        assert Project is OrigProject

    def test_exports_error_response(self) -> None:
        """Package should re-export ErrorResponse with correct identity."""
        from codeagent.mcp.models import ErrorResponse
        from codeagent.mcp.models.common import ErrorResponse as OrigErrorResponse

        assert ErrorResponse is OrigErrorResponse

    def test_exports_error_code(self) -> None:
        """Package should export ErrorCode."""
        from codeagent.mcp.models import ErrorCode

        assert ErrorCode.NOT_FOUND == "NOT_FOUND"
