"""Tests for ReflectionService - structured failure analysis and learning."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from codeagent.mcp.services.reflection_service import ReflectionService


def _make_service(
    db: AsyncMock | None = None,
    embedding: AsyncMock | None = None,
) -> tuple[ReflectionService, AsyncMock, AsyncMock]:
    """Create a ReflectionService with mock dependencies."""
    mock_db = db or AsyncMock()
    mock_embedding = embedding or AsyncMock()
    service = ReflectionService(db=mock_db, embedding=mock_embedding)
    return service, mock_db, mock_embedding


class TestReflect:
    """Tests for ReflectionService.reflect() method."""

    @pytest.mark.asyncio()
    async def test_reflect_stores_episode_memory(self) -> None:
        """reflect() should create a memory record with type 'episode'."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1, 0.2, 0.3]
        mock_db.create.return_value = [{"id": "memory:ep1"}]

        await service.reflect(
            output="failed output",
            feedback="AssertionError: expected 5 got 3",
            task="implement add function",
        )

        mock_db.create.assert_called_once()
        create_call = mock_db.create.call_args
        assert create_call[0][0] == "memory"
        data = create_call[0][1]
        assert data["type"] == "episode"

    @pytest.mark.asyncio()
    async def test_reflect_returns_structured_reflection(self) -> None:
        """reflect() should return a dict with what_went_wrong, root_cause, etc."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = [{"id": "memory:ep1"}]

        result = await service.reflect(
            output="bad output",
            feedback="test failed",
            task="fix parser",
            approach="regex approach",
        )

        assert "what_went_wrong" in result
        assert "root_cause" in result
        assert "what_to_try_next" in result
        assert "general_lesson" in result

    @pytest.mark.asyncio()
    async def test_reflect_includes_episode_id(self) -> None:
        """reflect() should return the created episode's ID."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = [{"id": "memory:ep42"}]

        result = await service.reflect(output="out", feedback="fb")

        assert result["episode_id"] == "memory:ep42"

    @pytest.mark.asyncio()
    async def test_reflect_handles_feedback_type(self) -> None:
        """reflect() should include feedback_type in metadata and response."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = [{"id": "memory:ep1"}]

        result = await service.reflect(
            output="out",
            feedback="lint error",
            feedback_type="lint_failure",
        )

        create_data = mock_db.create.call_args[0][1]
        assert create_data["metadata"]["feedback_type"] == "lint_failure"
        assert result["feedback_type"] == "lint_failure"

    @pytest.mark.asyncio()
    async def test_reflect_includes_model_used_in_tags(self) -> None:
        """reflect() should add model:X tag when model_used is provided."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = [{"id": "memory:ep1"}]

        await service.reflect(
            output="out",
            feedback="fb",
            model_used="opus",
        )

        create_data = mock_db.create.call_args[0][1]
        assert "model:opus" in create_data["tags"]

    @pytest.mark.asyncio()
    async def test_reflect_omits_model_tag_when_not_provided(self) -> None:
        """reflect() should not include model tag when model_used is None."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = [{"id": "memory:ep1"}]

        await service.reflect(output="out", feedback="fb")

        create_data = mock_db.create.call_args[0][1]
        assert not any(t.startswith("model:") for t in create_data["tags"])

    @pytest.mark.asyncio()
    async def test_reflect_embeds_content(self) -> None:
        """reflect() should embed the episode content before storing."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.5, 0.6]
        mock_db.create.return_value = [{"id": "memory:ep1"}]

        await service.reflect(
            output="out",
            feedback="fb",
            task="my task",
        )

        mock_embedding.embed.assert_called_once()
        create_data = mock_db.create.call_args[0][1]
        assert create_data["embedding"] == [0.5, 0.6]

    @pytest.mark.asyncio()
    async def test_reflect_handles_single_dict_from_create(self) -> None:
        """reflect() should handle when db.create returns a dict instead of list."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.create.return_value = {"id": "memory:single"}

        result = await service.reflect(output="out", feedback="fb")

        assert result["episode_id"] == "memory:single"


class TestImprovedAttempt:
    """Tests for ReflectionService.improved_attempt() method."""

    @pytest.mark.asyncio()
    async def test_improved_attempt_searches_episodes(self) -> None:
        """improved_attempt() should embed query and search for similar episodes."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.3, 0.4]
        mock_db.query.return_value = [{"result": []}]

        await service.improved_attempt(task="fix parser", original_output="broken")

        mock_embedding.embed.assert_called_once()
        mock_db.query.assert_called_once()
        query_str = mock_db.query.call_args[0][0]
        assert "episode" in query_str
        assert "cosine" in query_str

    @pytest.mark.asyncio()
    async def test_improved_attempt_returns_guidance_when_found(self) -> None:
        """improved_attempt() returns guidance with lessons."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [
            {
                "result": [
                    {
                        "id": "memory:ep1",
                        "score": 0.9,
                        "metadata": {
                            "reflection": {
                                "general_lesson": "Check edge cases",
                                "what_to_try_next": "Use boundary testing",
                            }
                        },
                    },
                ]
            }
        ]

        result = await service.improved_attempt(
            task="fix parser", original_output="broken"
        )

        assert "guidance" in result
        assert "similar_episodes" in result
        assert len(result["similar_episodes"]) == 1
        assert result["similar_episodes"][0]["lesson"] == "Check edge cases"
        assert result["confidence"] == 0.9

    @pytest.mark.asyncio()
    async def test_improved_attempt_returns_default_when_no_episodes(self) -> None:
        """improved_attempt() should return default guidance when no episodes match."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": []}]

        result = await service.improved_attempt(task="new task", original_output="out")

        assert "No similar past episodes" in result["guidance"]
        assert result["similar_episodes"] == []
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio()
    async def test_improved_attempt_includes_error_pattern_in_query(self) -> None:
        """improved_attempt() should include error_pattern in the embedding query."""
        service, mock_db, mock_embedding = _make_service()
        mock_embedding.embed.return_value = [0.1]
        mock_db.query.return_value = [{"result": []}]

        await service.improved_attempt(
            task="fix bug", original_output="out", error_pattern="TypeError"
        )

        embed_arg = mock_embedding.embed.call_args[0][0]
        assert "fix bug" in embed_arg
        assert "TypeError" in embed_arg


class TestModelEffectiveness:
    """Tests for ReflectionService.model_effectiveness() method."""

    @pytest.mark.asyncio()
    async def test_model_effectiveness_returns_recommended_model(self) -> None:
        """model_effectiveness() should return the model with highest success rate."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [
            {
                "result": [
                    {"model": "haiku", "outcome": "success"},
                    {"model": "haiku", "outcome": "success"},
                    {"model": "haiku", "outcome": "failure"},
                    {"model": "opus", "outcome": "success"},
                    {"model": "opus", "outcome": "failure"},
                    {"model": "opus", "outcome": "failure"},
                ]
            }
        ]

        result = await service.model_effectiveness(task_pattern="code generation")

        # haiku: 2/3 = 66%, opus: 1/3 = 33%
        assert result["recommended_model"] == "haiku"
        assert result["stats"]["haiku"]["success"] == 2
        assert result["stats"]["haiku"]["failure"] == 1
        assert result["stats"]["opus"]["success"] == 1

    @pytest.mark.asyncio()
    async def test_model_effectiveness_defaults_to_sonnet_with_no_data(self) -> None:
        """model_effectiveness() should default to sonnet when no episodes exist."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [{"result": []}]

        result = await service.model_effectiveness(task_pattern="anything")

        assert result["recommended_model"] == "sonnet"
        assert result["confidence"] == 0.0
        assert "No historical data" in result["reasoning"]

    @pytest.mark.asyncio()
    async def test_model_effectiveness_applies_feedback_type_filter(self) -> None:
        """model_effectiveness() should filter by feedback_type when provided."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [{"result": []}]

        await service.model_effectiveness(
            task_pattern="code gen", feedback_type="test_failure"
        )

        query_str = mock_db.query.call_args[0][0]
        assert "metadata.feedback_type = $ftype" in query_str
        params = mock_db.query.call_args[0][1]
        assert params["ftype"] == "test_failure"

    @pytest.mark.asyncio()
    async def test_model_effectiveness_calculates_success_rates(self) -> None:
        """model_effectiveness() should correctly compute success rates per model."""
        service, mock_db, _ = _make_service()
        mock_db.query.return_value = [
            {
                "result": [
                    {"model": "opus", "outcome": "success"},
                    {"model": "opus", "outcome": "success"},
                    {"model": "opus", "outcome": "success"},
                    {"model": "opus", "outcome": "failure"},
                ]
            }
        ]

        result = await service.model_effectiveness(task_pattern="test")

        assert result["recommended_model"] == "opus"
        assert result["confidence"] == 0.75  # 3/4
        assert result["stats"]["opus"]["total"] == 4
