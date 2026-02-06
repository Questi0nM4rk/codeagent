"""Tests for memory tool handlers.

Each tool function is tested for:
- Correct delegation to the underlying service
- Correct error handling (returns ErrorResponse on failure)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestInitMemoryTools:
    """Tests for init_memory_tools() setup."""

    def test_init_memory_tools_sets_services(self) -> None:
        """init_memory_tools should set the module-level service globals."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_mem = object()
        mock_search = object()
        mem_mod.init_memory_tools(mock_mem, mock_search)

        assert mem_mod._memory_service is mock_mem
        assert mem_mod._search_service is mock_search


class TestStore:
    """Tests for the store() tool function."""

    @pytest.mark.asyncio
    async def test_store_calls_memory_service(self) -> None:
        """store() should create a MemoryCreate and call _memory_service.store."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.store.return_value = {"memory_id": "memory:abc", "status": "created"}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.store(
                type="knowledge",
                content="test content",
                title="Test",
                tags=["tag1"],
                project="proj",
                confidence=0.9,
                source_task="task:1",
            )

        mock_svc.store.assert_awaited_once()
        call_arg = mock_svc.store.call_args[0][0]

        from codeagent.mcp.models import MemoryCreate, MemoryType

        assert isinstance(call_arg, MemoryCreate)
        assert call_arg.type == MemoryType.KNOWLEDGE
        assert call_arg.content == "test content"
        assert call_arg.title == "Test"
        assert call_arg.tags == ["tag1"]
        assert call_arg.project == "proj"
        assert call_arg.confidence == 0.9
        assert call_arg.source_task == "task:1"
        assert result == {"memory_id": "memory:abc", "status": "created"}

    @pytest.mark.asyncio
    async def test_store_returns_error_on_invalid_type(self) -> None:
        """store() with an invalid MemoryType string should return an ErrorResponse dict."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.store(type="INVALID_TYPE", content="test")

        assert "error" in result
        assert result["code"] == "VALIDATION_ERROR"
        mock_svc.store.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_store_returns_error_on_exception(self) -> None:
        """store() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.store.side_effect = RuntimeError("DB down")

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.store(type="knowledge", content="test")

        assert "error" in result
        assert "DB down" in result["error"]

    @pytest.mark.asyncio
    async def test_store_defaults_metadata_and_tags(self) -> None:
        """store() should default metadata to {} and tags to [] when not provided."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.store.return_value = {"memory_id": "memory:x"}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            await mem_mod.store(type="knowledge", content="test")

        call_arg = mock_svc.store.call_args[0][0]
        assert call_arg.metadata == {}
        assert call_arg.tags == []


class TestSearch:
    """Tests for the search() tool function."""

    @pytest.mark.asyncio
    async def test_search_calls_search_service(self) -> None:
        """search() should forward all parameters to _search_service.search."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.search.return_value = {"results": [], "total": 0}

        with patch.object(mem_mod, "_search_service", mock_svc):
            result = await mem_mod.search(
                query="test query",
                type="knowledge",
                project="proj",
                tags=["t1"],
                max_results=5,
                include_graph=True,
            )

        mock_svc.search.assert_awaited_once_with(
            query="test query",
            memory_type="knowledge",
            project="proj",
            tags=["t1"],
            max_results=5,
            include_graph=True,
        )
        assert result == {"results": [], "total": 0}

    @pytest.mark.asyncio
    async def test_search_returns_error_on_exception(self) -> None:
        """search() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.search.side_effect = RuntimeError("Search failed")

        with patch.object(mem_mod, "_search_service", mock_svc):
            result = await mem_mod.search(query="test")

        assert "error" in result
        assert "Search failed" in result["error"]
        assert result["code"] == "DB_ERROR"


class TestRead:
    """Tests for the read() tool function."""

    @pytest.mark.asyncio
    async def test_read_calls_memory_service(self) -> None:
        """read() should forward id and depth to _memory_service.read."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.read.return_value = {"memory_id": "memory:abc", "content": "data"}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.read(id="memory:abc", depth=2)

        mock_svc.read.assert_awaited_once_with("memory:abc", depth=2)
        assert result == {"memory_id": "memory:abc", "content": "data"}

    @pytest.mark.asyncio
    async def test_read_clamps_depth_to_3(self) -> None:
        """read() should clamp depth to a maximum of 3."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.read.return_value = {}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            await mem_mod.read(id="memory:abc", depth=10)

        mock_svc.read.assert_awaited_once_with("memory:abc", depth=3)

    @pytest.mark.asyncio
    async def test_read_returns_error_on_exception(self) -> None:
        """read() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.read.side_effect = RuntimeError("Not found")

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.read(id="memory:abc")

        assert "error" in result
        assert "Not found" in result["error"]
        assert result["code"] == "DB_ERROR"


class TestUpdate:
    """Tests for the update() tool function."""

    @pytest.mark.asyncio
    async def test_update_calls_memory_service(self) -> None:
        """update() should create a MemoryUpdate and call _memory_service.update."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.update.return_value = {"memory_id": "memory:abc", "status": "updated"}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.update(
                id="memory:abc",
                content="new content",
                title="New Title",
                metadata={"key": "value"},
                tags=["new_tag"],
                confidence=0.7,
            )

        mock_svc.update.assert_awaited_once()
        call_arg = mock_svc.update.call_args[0][0]

        from codeagent.mcp.models import MemoryUpdate

        assert isinstance(call_arg, MemoryUpdate)
        assert call_arg.memory_id == "memory:abc"
        assert call_arg.content == "new content"
        assert call_arg.title == "New Title"
        assert call_arg.metadata == {"key": "value"}
        assert call_arg.tags == ["new_tag"]
        assert call_arg.confidence == 0.7
        assert result == {"memory_id": "memory:abc", "status": "updated"}

    @pytest.mark.asyncio
    async def test_update_returns_error_on_exception(self) -> None:
        """update() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.update.side_effect = RuntimeError("Update failed")

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.update(id="memory:abc", content="new")

        assert "error" in result
        assert "Update failed" in result["error"]
        assert result["code"] == "DB_ERROR"


class TestDelete:
    """Tests for the delete() tool function."""

    @pytest.mark.asyncio
    async def test_delete_calls_memory_service(self) -> None:
        """delete() should forward id to _memory_service.delete."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.delete.return_value = {"status": "deleted"}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.delete(id="memory:abc")

        mock_svc.delete.assert_awaited_once_with("memory:abc")
        assert result == {"status": "deleted"}

    @pytest.mark.asyncio
    async def test_delete_returns_error_on_exception(self) -> None:
        """delete() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.delete.side_effect = RuntimeError("Delete failed")

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.delete(id="memory:abc")

        assert "error" in result
        assert "Delete failed" in result["error"]
        assert result["code"] == "DB_ERROR"


class TestLink:
    """Tests for the link() tool function."""

    @pytest.mark.asyncio
    async def test_link_calls_memory_service(self) -> None:
        """link() should forward from_id/to_id/reason/strength to _memory_service.link."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.link.return_value = {"status": "linked"}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.link(
                from_id="memory:a",
                to_id="memory:b",
                reason="related",
                strength=0.9,
            )

        mock_svc.link.assert_awaited_once_with("memory:a", "memory:b", "related", 0.9)
        assert result == {"status": "linked"}

    @pytest.mark.asyncio
    async def test_link_returns_error_on_exception(self) -> None:
        """link() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.link.side_effect = RuntimeError("Link failed")

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.link(from_id="memory:a", to_id="memory:b")

        assert "error" in result
        assert "Link failed" in result["error"]
        assert result["code"] == "DB_ERROR"


class TestStats:
    """Tests for the stats() tool function."""

    @pytest.mark.asyncio
    async def test_stats_calls_memory_service(self) -> None:
        """stats() should forward project/type to _memory_service.stats."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.stats.return_value = {"total": 42, "by_type": {}}

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.stats(project="proj", type="knowledge")

        mock_svc.stats.assert_awaited_once_with("proj", "knowledge")
        assert result == {"total": 42, "by_type": {}}

    @pytest.mark.asyncio
    async def test_stats_returns_error_on_exception(self) -> None:
        """stats() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import memory as mem_mod

        mock_svc = AsyncMock()
        mock_svc.stats.side_effect = RuntimeError("Stats failed")

        with patch.object(mem_mod, "_memory_service", mock_svc):
            result = await mem_mod.stats()

        assert "error" in result
        assert "Stats failed" in result["error"]
        assert result["code"] == "DB_ERROR"
