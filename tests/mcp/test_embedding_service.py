"""Tests for EmbeddingService - caching wrapper around EmbeddingProvider."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestEmbeddingServiceEmbed:
    """Tests for EmbeddingService.embed() method."""

    @pytest.mark.asyncio
    async def test_embed_returns_cached_value_on_hit(self) -> None:
        """embed() should return cached embedding without calling provider."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_cache = MagicMock()
        mock_cache.get.return_value = [0.1, 0.2, 0.3]

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed("hello world")

        assert result == [0.1, 0.2, 0.3]
        mock_cache.get.assert_called_once_with("hello world")
        mock_provider.embed.assert_not_called()

    @pytest.mark.asyncio
    async def test_embed_calls_provider_on_cache_miss(self) -> None:
        """embed() should call provider when cache misses and cache the result."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_provider.embed.return_value = [0.4, 0.5, 0.6]
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed("new text")

        assert result == [0.4, 0.5, 0.6]
        mock_provider.embed.assert_called_once_with("new text")
        mock_cache.put.assert_called_once_with("new text", [0.4, 0.5, 0.6])

    @pytest.mark.asyncio
    async def test_embed_does_not_cache_on_hit(self) -> None:
        """embed() should not call put() when cache hits."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_cache = MagicMock()
        mock_cache.get.return_value = [1.0, 2.0]

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        await service.embed("cached text")

        mock_cache.put.assert_not_called()

    @pytest.mark.asyncio
    async def test_embed_uses_default_cache_when_none_provided(self) -> None:
        """EmbeddingService should create a default EmbeddingCache when none given."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_provider.embed.return_value = [0.1]

        service = EmbeddingService(provider=mock_provider)
        assert isinstance(service._cache, EmbeddingCache)

    @pytest.mark.asyncio
    async def test_embed_returns_provider_result_type(self) -> None:
        """embed() should return a list of floats from the provider."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_provider.embed.return_value = [0.1, 0.2, 0.3, 0.4]
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed("test")

        assert isinstance(result, list)
        assert all(isinstance(v, float) for v in result)


class TestEmbeddingServiceEmbedBatch:
    """Tests for EmbeddingService.embed_batch() method."""

    @pytest.mark.asyncio
    async def test_embed_batch_all_cached(self) -> None:
        """embed_batch() should return all cached values without calling provider."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_cache = MagicMock()
        mock_cache.get.side_effect = [[0.1], [0.2], [0.3]]

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed_batch(["a", "b", "c"])

        assert result == [[0.1], [0.2], [0.3]]
        mock_provider.embed_batch.assert_not_called()

    @pytest.mark.asyncio
    async def test_embed_batch_all_misses(self) -> None:
        """embed_batch() should call provider for all texts when none cached."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_provider.embed_batch.return_value = [[0.1], [0.2]]
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed_batch(["x", "y"])

        assert result == [[0.1], [0.2]]
        mock_provider.embed_batch.assert_called_once_with(["x", "y"])

    @pytest.mark.asyncio
    async def test_embed_batch_partial_cache(self) -> None:
        """embed_batch() should only call provider for uncached texts."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_provider.embed_batch.return_value = [[0.5]]  # Only 1 miss
        mock_cache = MagicMock()
        # "a" cached, "b" not cached, "c" cached
        mock_cache.get.side_effect = [[0.1], None, [0.3]]

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed_batch(["a", "b", "c"])

        assert result == [[0.1], [0.5], [0.3]]
        mock_provider.embed_batch.assert_called_once_with(["b"])
        mock_cache.put.assert_called_once_with("b", [0.5])

    @pytest.mark.asyncio
    async def test_embed_batch_preserves_order(self) -> None:
        """embed_batch() must return results in same order as input texts."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        # Misses for indices 0 and 2
        mock_provider.embed_batch.return_value = [[1.0], [3.0]]
        mock_cache = MagicMock()
        mock_cache.get.side_effect = [None, [2.0], None]

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        result = await service.embed_batch(["first", "second", "third"])

        assert result == [[1.0], [2.0], [3.0]]

    @pytest.mark.asyncio
    async def test_embed_batch_caches_all_misses(self) -> None:
        """embed_batch() should cache every embedding from the provider."""
        from codeagent.mcp.services.embedding_service import EmbeddingService

        mock_provider = AsyncMock()
        mock_provider.embed_batch.return_value = [[0.1], [0.2]]
        mock_cache = MagicMock()
        mock_cache.get.return_value = None

        service = EmbeddingService(provider=mock_provider, cache=mock_cache)
        await service.embed_batch(["a", "b"])

        assert mock_cache.put.call_count == 2
        mock_cache.put.assert_any_call("a", [0.1])
        mock_cache.put.assert_any_call("b", [0.2])
