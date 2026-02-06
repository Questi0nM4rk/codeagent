"""Tests for SearchService - hybrid search over memories."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_service(
    db: AsyncMock | None = None,
    embedding: AsyncMock | None = None,
) -> tuple[object, AsyncMock, AsyncMock]:
    """Create a SearchService with mock dependencies."""
    from codeagent.mcp.services.search_service import SearchService

    mock_db = db or AsyncMock()
    mock_embedding = embedding or AsyncMock()
    service = SearchService(db=mock_db, embedding=mock_embedding)
    return service, mock_db, mock_embedding


class TestSearchServiceSearch:
    """Tests for SearchService.search() method."""

    @pytest.mark.asyncio
    async def test_search_embeds_query(self) -> None:
        """search() should embed the query string."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1, 0.2]
        mock_db.query.return_value = [{"result": []}]

        await service.search(query="find related patterns")

        mock_embedding.embed.assert_called_once_with("find related patterns")

    @pytest.mark.asyncio
    async def test_search_runs_vector_query(self) -> None:
        """search() should execute a vector similarity query."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": [
            {
                "id": "memory:abc",
                "type": "knowledge",
                "title": "Test",
                "content": "Short content",
                "vec_score": 0.95,
            }
        ]}]

        result = await service.search(query="test query")

        assert len(result["index"]) == 1
        assert result["index"][0]["id"] == "memory:abc"
        assert result["index"][0]["score"] == 0.95
        assert result["total_count"] == 1

    @pytest.mark.asyncio
    async def test_search_applies_type_filter(self) -> None:
        """search() should include type filter in the query."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": []}]

        await service.search(query="test", memory_type="knowledge")

        query_call = mock_db.query.call_args
        query_str = query_call[0][0]
        params = query_call[0][1]
        assert "type = $type" in query_str
        assert params["type"] == "knowledge"

    @pytest.mark.asyncio
    async def test_search_applies_project_filter(self) -> None:
        """search() should include project filter in the query."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": []}]

        await service.search(query="test", project="myproject")

        query_call = mock_db.query.call_args
        query_str = query_call[0][0]
        params = query_call[0][1]
        assert "project = $project" in query_str
        assert params["project"] == "myproject"

    @pytest.mark.asyncio
    async def test_search_applies_tags_filter(self) -> None:
        """search() should include tags filter in the query."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": []}]

        await service.search(query="test", tags=["python", "patterns"])

        query_call = mock_db.query.call_args
        query_str = query_call[0][0]
        params = query_call[0][1]
        assert "tags CONTAINS $tag0" in query_str
        assert "tags CONTAINS $tag1" in query_str
        assert params["tag0"] == "python"
        assert params["tag1"] == "patterns"

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_no_results(self) -> None:
        """search() should return empty structure when no results found."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": []}]

        result = await service.search(query="nothing here")

        assert result["index"] == []
        assert result["details"] == []
        assert result["total_count"] == 0

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_query_returns_none(self) -> None:
        """search() should handle None results from db.query."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = None

        result = await service.search(query="bad query")

        assert result["index"] == []
        assert result["details"] == []
        assert result["total_count"] == 0

    @pytest.mark.asyncio
    async def test_search_includes_graph_when_requested(self) -> None:
        """search() should include related memory IDs when include_graph=True."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.side_effect = [
            # Main search result
            [{"result": [
                {
                    "id": "memory:abc",
                    "type": "knowledge",
                    "title": "Test",
                    "content": "content",
                    "vec_score": 0.9,
                }
            ]}],
            # Graph traversal result
            [{"result": [{"related": ["memory:def"]}]}],
        ]

        result = await service.search(query="test", include_graph=True)

        assert len(result["details"]) == 1
        assert "related" in result["details"][0]

    @pytest.mark.asyncio
    async def test_search_truncates_long_content_for_snippets(self) -> None:
        """search() should truncate content > 200 chars with '...' for snippets."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        long_content = "x" * 300
        mock_db.query.return_value = [{"result": [
            {
                "id": "memory:abc",
                "type": "knowledge",
                "title": "Test",
                "content": long_content,
                "vec_score": 0.8,
            }
        ]}]

        result = await service.search(query="test")

        snippet = result["index"][0]["snippet"]
        assert len(snippet) == 203  # 200 chars + "..."
        assert snippet.endswith("...")

    @pytest.mark.asyncio
    async def test_search_keeps_short_content_as_snippet(self) -> None:
        """search() should not truncate content <= 200 chars."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": [
            {
                "id": "memory:abc",
                "type": "knowledge",
                "title": "Test",
                "content": "short",
                "vec_score": 0.8,
            }
        ]}]

        result = await service.search(query="test")

        assert result["index"][0]["snippet"] == "short"
