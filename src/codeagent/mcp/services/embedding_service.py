"""Embedding service with caching layer.

Thin wrapper combining EmbeddingProvider (API calls) with EmbeddingCache (LRU).
Checks cache before calling the provider, caches results on miss.
"""

from __future__ import annotations

from codeagent.mcp.embeddings.cache import EmbeddingCache
from codeagent.mcp.embeddings.provider import EmbeddingProvider


class EmbeddingService:
    """Embedding service with caching.

    Wraps an EmbeddingProvider with an optional EmbeddingCache to avoid
    redundant API calls for previously-seen texts.

    Args:
        provider: The underlying embedding provider (e.g. OpenAI).
        cache: Optional LRU cache. A default cache is created if not provided.
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        cache: EmbeddingCache | None = None,
    ) -> None:
        self._provider = provider
        self._cache = cache or EmbeddingCache()

    async def embed(self, text: str) -> list[float]:
        """Embed text. Check cache first, call provider on miss, cache result.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        cached = self._cache.get(text)
        if cached is not None:
            return cached
        result = await self._provider.embed(text)
        self._cache.put(text, result)
        return result

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts. Check cache for each, only call API for misses.

        Args:
            texts: The texts to embed.

        Returns:
            A list of embedding vectors in the same order as the input texts.
        """
        results: list[list[float] | None] = [self._cache.get(t) for t in texts]
        misses = [(i, t) for i, (t, r) in enumerate(zip(texts, results, strict=True)) if r is None]
        if misses:
            miss_texts = [t for _, t in misses]
            embeddings = await self._provider.embed_batch(miss_texts)
            for (idx, text), emb in zip(misses, embeddings, strict=True):
                results[idx] = emb
                self._cache.put(text, emb)
        return [r for r in results if r is not None]  # type narrowing
