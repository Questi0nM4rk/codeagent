"""Tests for models package exports."""

from __future__ import annotations


class TestModelsExports:
    """Verify that all models are exported from the models package."""

    def test_exports_memory_type(self) -> None:
        """Package should export MemoryType."""
        from codeagent.mcp.models import MemoryType

        assert MemoryType.KNOWLEDGE == "knowledge"

    def test_exports_memory(self) -> None:
        """Package should export Memory."""
        from codeagent.mcp.models import Memory

        assert Memory is not None

    def test_exports_memory_create(self) -> None:
        """Package should export MemoryCreate."""
        from codeagent.mcp.models import MemoryCreate

        assert MemoryCreate is not None

    def test_exports_memory_update(self) -> None:
        """Package should export MemoryUpdate."""
        from codeagent.mcp.models import MemoryUpdate

        assert MemoryUpdate is not None

    def test_exports_search_result(self) -> None:
        """Package should export SearchResult."""
        from codeagent.mcp.models import SearchResult

        assert SearchResult is not None

    def test_exports_search_response(self) -> None:
        """Package should export SearchResponse."""
        from codeagent.mcp.models import SearchResponse

        assert SearchResponse is not None

    def test_exports_task_status(self) -> None:
        """Package should export TaskStatus."""
        from codeagent.mcp.models import TaskStatus

        assert TaskStatus.PENDING == "pending"

    def test_exports_task_type(self) -> None:
        """Package should export TaskType."""
        from codeagent.mcp.models import TaskType

        assert TaskType.TASK == "task"

    def test_exports_task(self) -> None:
        """Package should export Task."""
        from codeagent.mcp.models import Task

        assert Task is not None

    def test_exports_task_create(self) -> None:
        """Package should export TaskCreate."""
        from codeagent.mcp.models import TaskCreate

        assert TaskCreate is not None

    def test_exports_project(self) -> None:
        """Package should export Project."""
        from codeagent.mcp.models import Project

        assert Project is not None

    def test_exports_error_response(self) -> None:
        """Package should export ErrorResponse."""
        from codeagent.mcp.models import ErrorResponse

        assert ErrorResponse is not None

    def test_exports_error_code(self) -> None:
        """Package should export ErrorCode."""
        from codeagent.mcp.models import ErrorCode

        assert ErrorCode.NOT_FOUND == "NOT_FOUND"
