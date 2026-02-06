"""Tests for memory Pydantic models."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError


class TestMemoryType:
    """Tests for MemoryType enum."""

    def test_memory_type_knowledge(self) -> None:
        """MemoryType must include knowledge."""
        from codeagent.mcp.models.memory import MemoryType

        assert MemoryType.KNOWLEDGE == "knowledge"

    def test_memory_type_episode(self) -> None:
        """MemoryType must include episode."""
        from codeagent.mcp.models.memory import MemoryType

        assert MemoryType.EPISODE == "episode"

    def test_memory_type_decision(self) -> None:
        """MemoryType must include decision."""
        from codeagent.mcp.models.memory import MemoryType

        assert MemoryType.DECISION == "decision"

    def test_memory_type_pattern(self) -> None:
        """MemoryType must include pattern."""
        from codeagent.mcp.models.memory import MemoryType

        assert MemoryType.PATTERN == "pattern"

    def test_memory_type_code_chunk(self) -> None:
        """MemoryType must include code_chunk."""
        from codeagent.mcp.models.memory import MemoryType

        assert MemoryType.CODE_CHUNK == "code_chunk"

    def test_memory_type_is_str_enum(self) -> None:
        """MemoryType values should be usable as strings."""
        from codeagent.mcp.models.memory import MemoryType

        assert isinstance(MemoryType.KNOWLEDGE, str)


class TestMemory:
    """Tests for the Memory model."""

    def test_create_memory_with_required_fields(self) -> None:
        """Memory should be constructable with required fields only."""
        from codeagent.mcp.models.memory import Memory, MemoryType

        now = datetime.now(tz=UTC)
        mem = Memory(
            type=MemoryType.KNOWLEDGE,
            content="Repository pattern in Python",
            embedding=[0.1] * 1536,
            created_at=now,
            updated_at=now,
        )
        assert mem.content == "Repository pattern in Python"
        assert mem.type == MemoryType.KNOWLEDGE
        assert len(mem.embedding) == 1536

    def test_memory_has_optional_id(self) -> None:
        """Memory.memory_id should default to None."""
        from codeagent.mcp.models.memory import Memory, MemoryType

        now = datetime.now(tz=UTC)
        mem = Memory(
            type=MemoryType.KNOWLEDGE,
            content="test",
            embedding=[],
            created_at=now,
            updated_at=now,
        )
        assert mem.memory_id is None

    def test_memory_id_can_be_set(self) -> None:
        """Memory.memory_id can be set to a SurrealDB record ID."""
        from codeagent.mcp.models.memory import Memory, MemoryType

        now = datetime.now(tz=UTC)
        mem = Memory(
            memory_id="memory:abc123",
            type=MemoryType.EPISODE,
            content="test",
            embedding=[],
            created_at=now,
            updated_at=now,
        )
        assert mem.memory_id == "memory:abc123"

    def test_memory_defaults(self) -> None:
        """Memory should have sensible defaults for optional fields."""
        from codeagent.mcp.models.memory import Memory, MemoryType

        now = datetime.now(tz=UTC)
        mem = Memory(
            type=MemoryType.KNOWLEDGE,
            content="test",
            embedding=[],
            created_at=now,
            updated_at=now,
        )
        assert mem.title is None
        assert mem.metadata == {}
        assert mem.tags == []
        assert mem.project is None
        assert mem.confidence == 1.0
        assert mem.access_count == 0
        assert mem.last_accessed is None
        assert mem.source_task is None

    def test_memory_serializes_to_dict(self) -> None:
        """Memory should serialize cleanly to a dict."""
        from codeagent.mcp.models.memory import Memory, MemoryType

        now = datetime.now(tz=UTC)
        mem = Memory(
            type=MemoryType.DECISION,
            content="Use JWT",
            embedding=[0.5],
            tags=["auth"],
            project="myproject",
            created_at=now,
            updated_at=now,
        )
        data = mem.model_dump()
        assert data["type"] == "decision"
        assert data["tags"] == ["auth"]
        assert data["project"] == "myproject"

    def test_memory_rejects_invalid_type(self) -> None:
        """Memory should reject an invalid type value."""
        from codeagent.mcp.models.memory import Memory

        now = datetime.now(tz=UTC)
        with pytest.raises(ValidationError):
            Memory(
                type="invalid_type",  # type: ignore[arg-type]
                content="test",
                embedding=[],
                created_at=now,
                updated_at=now,
            )


class TestMemoryCreate:
    """Tests for the MemoryCreate input model."""

    def test_create_with_minimal_fields(self) -> None:
        """MemoryCreate should work with just content and type."""
        from codeagent.mcp.models.memory import MemoryCreate, MemoryType

        create = MemoryCreate(content="test content", type=MemoryType.KNOWLEDGE)
        assert create.content == "test content"
        assert create.type == MemoryType.KNOWLEDGE

    def test_create_defaults(self) -> None:
        """MemoryCreate should have sensible defaults."""
        from codeagent.mcp.models.memory import MemoryCreate, MemoryType

        create = MemoryCreate(content="test", type=MemoryType.PATTERN)
        assert create.title is None
        assert create.metadata == {}
        assert create.tags == []
        assert create.project is None
        assert create.confidence == 1.0
        assert create.source_task is None

    def test_create_with_all_fields(self) -> None:
        """MemoryCreate should accept all optional fields."""
        from codeagent.mcp.models.memory import MemoryCreate, MemoryType

        create = MemoryCreate(
            content="test",
            type=MemoryType.EPISODE,
            title="My Episode",
            metadata={"outcome": "success"},
            tags=["testing"],
            project="codeagent",
            confidence=0.8,
            source_task="task:abc",
        )
        assert create.title == "My Episode"
        assert create.metadata == {"outcome": "success"}
        assert create.tags == ["testing"]
        assert create.confidence == 0.8
        assert create.source_task == "task:abc"

    def test_create_requires_content(self) -> None:
        """MemoryCreate should require content."""
        from codeagent.mcp.models.memory import MemoryCreate, MemoryType

        with pytest.raises(ValidationError):
            MemoryCreate(type=MemoryType.KNOWLEDGE)  # type: ignore[call-arg]

    def test_create_requires_type(self) -> None:
        """MemoryCreate should require type."""
        from codeagent.mcp.models.memory import MemoryCreate

        with pytest.raises(ValidationError):
            MemoryCreate(content="test")  # type: ignore[call-arg]


class TestMemoryUpdate:
    """Tests for the MemoryUpdate input model."""

    def test_update_all_optional_except_id(self) -> None:
        """MemoryUpdate should have all optional fields except memory_id."""
        from codeagent.mcp.models.memory import MemoryUpdate

        update = MemoryUpdate(memory_id="memory:abc")
        assert update.memory_id == "memory:abc"
        assert update.content is None
        assert update.title is None
        assert update.metadata is None
        assert update.tags is None
        assert update.confidence is None

    def test_update_with_partial_fields(self) -> None:
        """MemoryUpdate should accept partial updates."""
        from codeagent.mcp.models.memory import MemoryUpdate

        update = MemoryUpdate(
            memory_id="memory:abc",
            content="updated content",
            confidence=0.9,
        )
        assert update.content == "updated content"
        assert update.confidence == 0.9
        assert update.tags is None

    def test_update_requires_memory_id(self) -> None:
        """MemoryUpdate should require memory_id."""
        from codeagent.mcp.models.memory import MemoryUpdate

        with pytest.raises(ValidationError):
            MemoryUpdate(content="update without id")  # type: ignore[call-arg]


class TestSearchResult:
    """Tests for the SearchResult model."""

    def test_search_result_fields(self) -> None:
        """SearchResult should hold id, title, type, score, snippet."""
        from codeagent.mcp.models.memory import MemoryType, SearchResult

        result = SearchResult(
            id="memory:abc",
            title="My Memory",
            type=MemoryType.KNOWLEDGE,
            score=0.95,
            snippet="Repository pattern...",
        )
        assert result.id == "memory:abc"
        assert result.title == "My Memory"
        assert result.type == MemoryType.KNOWLEDGE
        assert result.score == 0.95
        assert result.snippet == "Repository pattern..."

    def test_search_result_title_optional(self) -> None:
        """SearchResult.title can be None."""
        from codeagent.mcp.models.memory import MemoryType, SearchResult

        result = SearchResult(
            id="memory:abc",
            title=None,
            type=MemoryType.EPISODE,
            score=0.5,
            snippet="...",
        )
        assert result.title is None


class TestSearchResponse:
    """Tests for the SearchResponse model."""

    def test_search_response_structure(self) -> None:
        """SearchResponse should have index, details, and total_count."""
        from codeagent.mcp.models.memory import (
            Memory,
            MemoryType,
            SearchResponse,
            SearchResult,
        )

        now = datetime.now(tz=UTC)
        result = SearchResult(
            id="memory:abc",
            title="Test",
            type=MemoryType.KNOWLEDGE,
            score=0.9,
            snippet="test snippet",
        )
        detail = Memory(
            memory_id="memory:abc",
            type=MemoryType.KNOWLEDGE,
            content="full content",
            embedding=[],
            created_at=now,
            updated_at=now,
        )
        response = SearchResponse(
            index=[result],
            details=[detail],
            total_count=1,
        )
        assert len(response.index) == 1
        assert len(response.details) == 1
        assert response.total_count == 1

    def test_search_response_empty(self) -> None:
        """SearchResponse should handle empty results."""
        from codeagent.mcp.models.memory import SearchResponse

        response = SearchResponse(index=[], details=[], total_count=0)
        assert response.index == []
        assert response.details == []
        assert response.total_count == 0
