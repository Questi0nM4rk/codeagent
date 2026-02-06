"""Tests for MemoryService - business logic for memory CRUD."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


def _make_memory_create(**overrides: object) -> object:
    """Create a MemoryCreate instance with defaults."""
    from codeagent.mcp.models.memory import MemoryCreate, MemoryType

    defaults = {
        "content": "Test memory content",
        "type": MemoryType.KNOWLEDGE,
        "title": "Test Memory",
        "tags": ["test"],
        "project": "testproject",
    }
    defaults.update(overrides)
    return MemoryCreate(**defaults)  # type: ignore[arg-type]


def _make_memory_update(**overrides: object) -> object:
    """Create a MemoryUpdate instance with defaults."""
    from codeagent.mcp.models.memory import MemoryUpdate

    defaults = {"memory_id": "memory:abc123"}
    defaults.update(overrides)
    return MemoryUpdate(**defaults)  # type: ignore[arg-type]


def _make_service(
    db: AsyncMock | None = None,
    embedding: AsyncMock | None = None,
) -> tuple[object, AsyncMock, AsyncMock]:
    """Create a MemoryService with mock dependencies."""
    from codeagent.mcp.services.memory_service import MemoryService

    mock_db = db or AsyncMock()
    mock_embedding = embedding or AsyncMock()
    service = MemoryService(db=mock_db, embedding=mock_embedding)
    return service, mock_db, mock_embedding


class TestMemoryServiceStore:
    """Tests for MemoryService.store() method."""

    @pytest.mark.asyncio
    async def test_store_embeds_content(self) -> None:
        """store() should embed the content before inserting."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1, 0.2, 0.3]
        mock_db.create.return_value = [{"id": "memory:abc"}]
        mock_db.query.return_value = None  # auto-link returns nothing

        create = _make_memory_create()
        await service.store(create)

        mock_embedding.embed.assert_called_once_with("Test memory content")

    @pytest.mark.asyncio
    async def test_store_inserts_into_db_with_embedding(self) -> None:
        """store() should pass embedded vector to db.create."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1, 0.2]
        mock_db.create.return_value = [{"id": "memory:abc"}]
        mock_db.query.return_value = None

        create = _make_memory_create()
        await service.store(create)

        create_call = mock_db.create.call_args
        assert create_call[0][0] == "memory"
        data = create_call[0][1]
        assert data["embedding"] == [0.1, 0.2]
        assert data["content"] == "Test memory content"

    @pytest.mark.asyncio
    async def test_store_calls_auto_link(self) -> None:
        """store() should call _auto_link after creating the record."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.5]
        mock_db.create.return_value = [{"id": "memory:new123"}]
        # auto_link will call query twice (search + relate)
        mock_db.query.return_value = [{"result": [{"id": "memory:old1", "score": 0.9}]}]

        create = _make_memory_create()
        await service.store(create)

        # Should have queried for similar memories
        query_calls = mock_db.query.call_args_list
        assert len(query_calls) >= 1  # At least the similarity search

    @pytest.mark.asyncio
    async def test_store_returns_created_record(self) -> None:
        """store() should return the created record dict."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = [{"id": "memory:xyz", "content": "test"}]
        mock_db.query.return_value = None

        create = _make_memory_create()
        result = await service.store(create)

        assert result == {"id": "memory:xyz", "content": "test"}

    @pytest.mark.asyncio
    async def test_store_handles_single_dict_from_create(self) -> None:
        """store() should handle when db.create returns a dict instead of list."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = {"id": "memory:single"}
        mock_db.query.return_value = None

        create = _make_memory_create()
        result = await service.store(create)

        assert result["id"] == "memory:single"


class TestMemoryServiceRead:
    """Tests for MemoryService.read() method."""

    @pytest.mark.asyncio
    async def test_read_increments_access_count(self) -> None:
        """read() should increment access_count via query."""
        service, mock_db, _ = _make_service()
        mock_db.select.return_value = {"id": "memory:abc", "content": "test"}
        mock_db.query.return_value = None

        await service.read("memory:abc")

        # First query call should be the access_count update
        first_query = mock_db.query.call_args_list[0]
        assert "access_count" in first_query[0][0]
        assert first_query[0][1] == {"id": "memory:abc"}

    @pytest.mark.asyncio
    async def test_read_returns_not_found_for_missing_id(self) -> None:
        """read() should return error dict when memory not found."""
        service, mock_db, _ = _make_service()
        mock_db.select.return_value = None
        mock_db.query.return_value = None

        result = await service.read("memory:nonexistent")

        assert result["error"] == "Memory not found"
        assert result["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_read_returns_memory_data(self) -> None:
        """read() should return the memory record on success."""
        service, mock_db, _ = _make_service()
        mock_db.select.return_value = {"id": "memory:abc", "content": "hello"}
        mock_db.query.return_value = None

        result = await service.read("memory:abc", depth=0)

        assert result["id"] == "memory:abc"
        assert result["content"] == "hello"

    @pytest.mark.asyncio
    async def test_read_includes_related_when_depth_gt_zero(self) -> None:
        """read() should include related_memories when depth > 0."""
        service, mock_db, _ = _make_service()
        mock_db.select.return_value = {"id": "memory:abc", "content": "hello"}
        mock_db.query.side_effect = [
            None,  # access_count update
            [{"result": [{"id": "memory:related1"}]}],  # graph traversal
        ]

        result = await service.read("memory:abc", depth=1)

        assert "related_memories" in result
        assert result["related_memories"] == [{"id": "memory:related1"}]

    @pytest.mark.asyncio
    async def test_read_skips_graph_when_depth_zero(self) -> None:
        """read() should not query graph when depth=0."""
        service, mock_db, _ = _make_service()
        mock_db.select.return_value = {"id": "memory:abc", "content": "test"}
        mock_db.query.return_value = None

        result = await service.read("memory:abc", depth=0)

        # Only the access_count query should have been called
        assert mock_db.query.call_count == 1
        assert "related_memories" not in result


class TestMemoryServiceUpdate:
    """Tests for MemoryService.update() method."""

    @pytest.mark.asyncio
    async def test_update_reembeds_when_content_changes(self) -> None:
        """update() should re-embed when content is provided."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.9, 0.8]
        mock_db.update.return_value = {"id": "memory:abc", "content": "updated"}

        update = _make_memory_update(content="updated content")
        await service.update(update)

        mock_embedding.embed.assert_called_once_with("updated content")
        update_call = mock_db.update.call_args
        assert update_call[0][1]["embedding"] == [0.9, 0.8]

    @pytest.mark.asyncio
    async def test_update_skips_embedding_for_metadata_only(self) -> None:
        """update() should not re-embed when only metadata fields change."""
        service, mock_db, mock_embedding = _make_service()
        mock_db.update.return_value = {"id": "memory:abc"}

        update = _make_memory_update(title="New Title", confidence=0.9)
        await service.update(update)

        mock_embedding.embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_sets_updated_at(self) -> None:
        """update() should set the updated_at timestamp."""
        service, mock_db, mock_embedding = _make_service()
        mock_db.update.return_value = {"id": "memory:abc"}

        update = _make_memory_update(title="New Title")
        await service.update(update)

        update_call = mock_db.update.call_args
        assert "updated_at" in update_call[0][1]

    @pytest.mark.asyncio
    async def test_update_returns_result(self) -> None:
        """update() should return the updated record."""
        service, mock_db, mock_embedding = _make_service()
        mock_db.update.return_value = {"id": "memory:abc", "title": "Updated"}

        update = _make_memory_update(title="Updated")
        result = await service.update(update)

        assert result == {"id": "memory:abc", "title": "Updated"}


class TestMemoryServiceDelete:
    """Tests for MemoryService.delete() method."""

    @pytest.mark.asyncio
    async def test_delete_calls_db_delete(self) -> None:
        """delete() should call db.delete with the memory_id."""
        service, mock_db, _ = _make_service()
        mock_db.delete.return_value = {"id": "memory:abc"}

        result = await service.delete("memory:abc")

        mock_db.delete.assert_called_once_with("memory:abc")
        assert result["deleted"] == "memory:abc"

    @pytest.mark.asyncio
    async def test_delete_returns_confirmation(self) -> None:
        """delete() should return a dict with deleted key."""
        service, mock_db, _ = _make_service()
        mock_db.delete.return_value = {"id": "memory:abc"}

        result = await service.delete("memory:abc")

        assert "deleted" in result
        assert "result" in result


class TestMemoryServiceLink:
    """Tests for MemoryService.link() method."""

    @pytest.mark.asyncio
    async def test_link_creates_relates_to_edge(self) -> None:
        """link() should execute RELATE query to create edge."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [{"result": "ok"}]

        await service.link(
            from_id="memory:a",
            to_id="memory:b",
            reason="related concept",
            strength=0.9,
        )

        query_call = mock_db.query.call_args
        assert "RELATE" in query_call[0][0]
        assert "relates_to" in query_call[0][0]
        params = query_call[0][1]
        assert params["from"] == "memory:a"
        assert params["to"] == "memory:b"
        assert params["strength"] == 0.9
        assert params["reason"] == "related concept"

    @pytest.mark.asyncio
    async def test_link_returns_success(self) -> None:
        """link() should return a dict indicating success."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [{"result": "ok"}]

        result = await service.link("memory:a", "memory:b")

        assert result["linked"] is True


class TestMemoryServiceStats:
    """Tests for MemoryService.stats() method."""

    @pytest.mark.asyncio
    async def test_stats_returns_correct_aggregates(self) -> None:
        """stats() should return total, by_type, and by_project."""
        service, mock_db, _ = _make_service()
        mock_db.query.side_effect = [
            [{"result": [{"total": 42}]}],
            [{"result": [{"type": "knowledge", "count": 30}, {"type": "episode", "count": 12}]}],
            [{"result": [{"project": "proj1", "count": 25}, {"project": "proj2", "count": 17}]}],
        ]

        result = await service.stats()

        assert result["total"] == 42
        assert result["by_type"] == {"knowledge": 30, "episode": 12}
        assert result["by_project"] == {"proj1": 25, "proj2": 17}

    @pytest.mark.asyncio
    async def test_stats_applies_project_filter(self) -> None:
        """stats() should include project filter in queries."""
        service, mock_db, _ = _make_service()
        mock_db.query.side_effect = [
            [{"result": [{"total": 10}]}],
            [{"result": [{"type": "knowledge", "count": 10}]}],
            [{"result": [{"project": "myproj", "count": 10}]}],
        ]

        await service.stats(project="myproj")

        for query_call in mock_db.query.call_args_list:
            query_str = query_call[0][0]
            assert "project = $project" in query_str
            assert query_call[0][1]["project"] == "myproj"

    @pytest.mark.asyncio
    async def test_stats_applies_type_filter(self) -> None:
        """stats() should include type filter in queries."""
        service, mock_db, _ = _make_service()
        mock_db.query.side_effect = [
            [{"result": [{"total": 5}]}],
            [{"result": [{"type": "episode", "count": 5}]}],
            [{"result": []}],
        ]

        await service.stats(memory_type="episode")

        for query_call in mock_db.query.call_args_list:
            query_str = query_call[0][0]
            assert "type = $type" in query_str
            assert query_call[0][1]["type"] == "episode"

    @pytest.mark.asyncio
    async def test_stats_returns_zero_when_empty(self) -> None:
        """stats() should return 0 total when no results."""
        service, mock_db, _ = _make_service()
        mock_db.query.side_effect = [
            [{"result": []}],  # empty total
            [{"result": []}],
            [{"result": []}],
        ]

        result = await service.stats()

        assert result["total"] == 0
        assert result["by_type"] == {}
        assert result["by_project"] == {}


class TestMemoryServiceAutoLink:
    """Tests for MemoryService._auto_link() private method."""

    @pytest.mark.asyncio
    async def test_auto_link_creates_edges_for_similar_memories(self) -> None:
        """_auto_link() should create relates_to edges for high-similarity matches."""
        service, mock_db, _ = _make_service()
        mock_db.query.side_effect = [
            # Similarity search result
            [
                {
                    "result": [
                        {"id": "memory:similar1", "score": 0.9},
                        {"id": "memory:similar2", "score": 0.8},
                    ]
                }
            ],
            # RELATE calls
            [{"result": "ok"}],
            [{"result": "ok"}],
        ]

        await service._auto_link("memory:new", [0.1, 0.2])

        # Should have called query for similarity search + 2 RELATE statements
        assert mock_db.query.call_count == 3

    @pytest.mark.asyncio
    async def test_auto_link_skips_low_similarity(self) -> None:
        """_auto_link() should not create edges when similarity < 0.7."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [
            {
                "result": [
                    {"id": "memory:weak", "score": 0.3},
                ]
            }
        ]

        await service._auto_link("memory:new", [0.1])

        # Only the similarity search query, no RELATE
        assert mock_db.query.call_count == 1
