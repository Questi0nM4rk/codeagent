"""Tests for the embedding service (provider and cache)."""

from __future__ import annotations

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


def _make_httpx_mock(
    *,
    status_code: int = 200,
    json_data: dict[str, object] | None = None,
    raise_for_status_effect: Exception | None = None,
) -> tuple[AsyncMock, MagicMock]:
    """Create a mock httpx.AsyncClient and Response pair.

    Returns:
        A tuple of (mock_client, mock_response).
    """
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = status_code
    if raise_for_status_effect is not None:
        mock_response.raise_for_status.side_effect = raise_for_status_effect
    else:
        mock_response.raise_for_status = MagicMock()
    if json_data is not None:
        mock_response.json.return_value = json_data

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    return mock_client, mock_response


# ---------------------------------------------------------------------------
# EmbeddingProvider tests
# ---------------------------------------------------------------------------


class TestEmbeddingProviderInit:
    """Tests for EmbeddingProvider initialization."""

    def test_init_with_explicit_api_key(self) -> None:
        """EmbeddingProvider accepts an explicit API key."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        provider = EmbeddingProvider(api_key="sk-test-key")
        assert provider._api_key == "sk-test-key"

    def test_init_reads_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """EmbeddingProvider reads OPENAI_API_KEY from environment when no key given."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key")
        provider = EmbeddingProvider()
        assert provider._api_key == "sk-env-key"

    def test_init_raises_when_no_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """EmbeddingProvider raises ValueError when no API key is available."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key"):
            EmbeddingProvider()

    def test_model_and_dimensions_constants(self) -> None:
        """EmbeddingProvider exposes correct model name and dimensions."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        assert EmbeddingProvider.MODEL == "text-embedding-3-small"
        assert EmbeddingProvider.DIMENSIONS == 1536


class TestEmbeddingProviderEmbed:
    """Tests for EmbeddingProvider.embed() single-text embedding."""

    @pytest.mark.asyncio
    async def test_embed_returns_embedding_vector(self) -> None:
        """embed() returns a list of floats from the OpenAI API response."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        expected_embedding = [0.1, 0.2, 0.3]
        mock_client, _mock_response = _make_httpx_mock(
            json_data={"data": [{"embedding": expected_embedding, "index": 0}]},
        )

        with patch("codeagent.mcp.embeddings.provider.httpx.AsyncClient", return_value=mock_client):
            provider = EmbeddingProvider(api_key="sk-test")
            result = await provider.embed("hello world")

        assert result == expected_embedding

    @pytest.mark.asyncio
    async def test_embed_sends_correct_api_request(self) -> None:
        """embed() sends the correct payload to OpenAI's API."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        mock_client, _mock_response = _make_httpx_mock(
            json_data={"data": [{"embedding": [0.0], "index": 0}]},
        )

        with patch(
            "codeagent.mcp.embeddings.provider.httpx.AsyncClient",
            return_value=mock_client,
        ) as mock_cls:
            provider = EmbeddingProvider(api_key="sk-test")
            await provider.embed("test text")

        # Headers are now pre-set on the reusable client at construction time
        ctor_kwargs = mock_cls.call_args[1]
        assert ctor_kwargs["headers"]["Authorization"] == "Bearer sk-test"
        assert ctor_kwargs["headers"]["Content-Type"] == "application/json"

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://api.openai.com/v1/embeddings"

        payload = call_args[1]["json"]
        assert payload["input"] == ["test text"]
        assert payload["model"] == "text-embedding-3-small"
        assert payload["dimensions"] == 1536

    @pytest.mark.asyncio
    async def test_embed_raises_on_api_error(self) -> None:
        """embed() propagates httpx.HTTPStatusError on API failure."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        mock_request = MagicMock(spec=httpx.Request)
        mock_error_response = MagicMock(spec=httpx.Response)
        mock_error_response.status_code = 401

        mock_client, _mock_response = _make_httpx_mock(
            status_code=401,
            raise_for_status_effect=httpx.HTTPStatusError(
                "Unauthorized",
                request=mock_request,
                response=mock_error_response,
            ),
        )

        with patch("codeagent.mcp.embeddings.provider.httpx.AsyncClient", return_value=mock_client):
            provider = EmbeddingProvider(api_key="sk-bad")
            with pytest.raises(httpx.HTTPStatusError):
                await provider.embed("test")


class TestEmbeddingProviderEmbedBatch:
    """Tests for EmbeddingProvider.embed_batch() multi-text embedding."""

    @pytest.mark.asyncio
    async def test_embed_batch_returns_ordered_embeddings(self) -> None:
        """embed_batch() returns embeddings sorted by index regardless of API order."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        # API may return results out of order
        mock_client, _mock_response = _make_httpx_mock(
            json_data={
                "data": [
                    {"embedding": [0.3, 0.3], "index": 2},
                    {"embedding": [0.1, 0.1], "index": 0},
                    {"embedding": [0.2, 0.2], "index": 1},
                ],
            },
        )

        with patch("codeagent.mcp.embeddings.provider.httpx.AsyncClient", return_value=mock_client):
            provider = EmbeddingProvider(api_key="sk-test")
            result = await provider.embed_batch(["a", "b", "c"])

        assert len(result) == 3
        assert result[0] == [0.1, 0.1]
        assert result[1] == [0.2, 0.2]
        assert result[2] == [0.3, 0.3]

    @pytest.mark.asyncio
    async def test_embed_batch_sends_all_texts_in_single_request(self) -> None:
        """embed_batch() sends all texts in one API call."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        mock_client, _mock_response = _make_httpx_mock(
            json_data={
                "data": [
                    {"embedding": [0.0], "index": 0},
                    {"embedding": [0.0], "index": 1},
                ],
            },
        )

        with patch("codeagent.mcp.embeddings.provider.httpx.AsyncClient", return_value=mock_client):
            provider = EmbeddingProvider(api_key="sk-test")
            await provider.embed_batch(["text1", "text2"])

        mock_client.post.assert_called_once()
        payload = mock_client.post.call_args[1]["json"]
        assert payload["input"] == ["text1", "text2"]

    @pytest.mark.asyncio
    async def test_embed_batch_raises_on_api_error(self) -> None:
        """embed_batch() propagates httpx.HTTPStatusError on API failure."""
        from codeagent.mcp.embeddings.provider import EmbeddingProvider

        mock_request = MagicMock(spec=httpx.Request)
        mock_error_response = MagicMock(spec=httpx.Response)
        mock_error_response.status_code = 500

        mock_client, _mock_response = _make_httpx_mock(
            status_code=500,
            raise_for_status_effect=httpx.HTTPStatusError(
                "Server Error",
                request=mock_request,
                response=mock_error_response,
            ),
        )

        with patch("codeagent.mcp.embeddings.provider.httpx.AsyncClient", return_value=mock_client):
            provider = EmbeddingProvider(api_key="sk-test")
            with pytest.raises(httpx.HTTPStatusError):
                await provider.embed_batch(["a", "b"])


# ---------------------------------------------------------------------------
# EmbeddingCache tests
# ---------------------------------------------------------------------------


class TestEmbeddingCacheGetPut:
    """Tests for EmbeddingCache get/put operations."""

    def test_get_returns_none_on_cache_miss(self) -> None:
        """get() returns None when content has not been cached."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache()
        assert cache.get("never seen") is None

    def test_put_then_get_returns_cached_embedding(self) -> None:
        """put() stores embedding and get() retrieves it by content."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache()
        embedding = [0.1, 0.2, 0.3]
        cache.put("hello", embedding)
        assert cache.get("hello") == embedding

    def test_get_returns_none_for_different_content(self) -> None:
        """get() returns None for content that differs from what was put."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache()
        cache.put("hello", [0.1, 0.2])
        assert cache.get("world") is None


class TestEmbeddingCacheEviction:
    """Tests for EmbeddingCache LRU eviction behavior."""

    def test_evicts_oldest_when_max_size_reached(self) -> None:
        """Cache evicts least-recently-used entry when max_size is exceeded."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache(max_size=2)
        cache.put("a", [1.0])
        cache.put("b", [2.0])
        cache.put("c", [3.0])  # should evict "a"

        assert cache.get("a") is None
        assert cache.get("b") == [2.0]
        assert cache.get("c") == [3.0]

    def test_accessing_entry_prevents_eviction(self) -> None:
        """Accessing an entry via get() makes it recently used, preventing eviction."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache(max_size=2)
        cache.put("a", [1.0])
        cache.put("b", [2.0])
        cache.get("a")  # touch "a" so it becomes most recently used
        cache.put("c", [3.0])  # should evict "b" (now oldest)

        assert cache.get("a") == [1.0]
        assert cache.get("b") is None
        assert cache.get("c") == [3.0]


class TestEmbeddingCacheHash:
    """Tests for EmbeddingCache hash consistency."""

    def test_hash_is_sha256_of_content(self) -> None:
        """_hash() returns the SHA-256 hex digest of the input content."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache()
        content = "hello world"
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert cache._hash(content) == expected

    def test_same_content_produces_same_hash(self) -> None:
        """_hash() is deterministic -- same input always gives same hash."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache()
        assert cache._hash("test") == cache._hash("test")

    def test_different_content_produces_different_hash(self) -> None:
        """_hash() produces different hashes for different inputs."""
        from codeagent.mcp.embeddings.cache import EmbeddingCache

        cache = EmbeddingCache()
        assert cache._hash("foo") != cache._hash("bar")


# ---------------------------------------------------------------------------
# __init__.py exports test
# ---------------------------------------------------------------------------


class TestEmbeddingsPackageExports:
    """Tests that the embeddings package exports expected symbols."""

    def test_exports_embedding_provider(self) -> None:
        """embeddings package re-exports EmbeddingProvider with correct identity."""
        from codeagent.mcp.embeddings import EmbeddingProvider
        from codeagent.mcp.embeddings.provider import (
            EmbeddingProvider as OrigEmbeddingProvider,
        )

        assert EmbeddingProvider is OrigEmbeddingProvider

    def test_exports_embedding_cache(self) -> None:
        """embeddings package re-exports EmbeddingCache with correct identity."""
        from codeagent.mcp.embeddings import EmbeddingCache
        from codeagent.mcp.embeddings.cache import EmbeddingCache as OrigEmbeddingCache

        assert EmbeddingCache is OrigEmbeddingCache
