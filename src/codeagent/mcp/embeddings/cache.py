"""In-memory LRU cache for embedding vectors."""

from __future__ import annotations

from collections import OrderedDict
import hashlib


class EmbeddingCache:
    """In-memory LRU cache for embeddings, keyed by content hash.

    Avoids redundant API calls by caching embeddings for content that has
    already been seen. Uses SHA-256 hashing so that identical content always
    maps to the same cache key.

    Example::

        cache = EmbeddingCache(max_size=500)
        cache.put("hello", [0.1, 0.2, 0.3])
        vec = cache.get("hello")  # [0.1, 0.2, 0.3]
    """

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize the cache.

        Args:
            max_size: Maximum number of entries before LRU eviction kicks in.
        """
        self._max_size = max_size
        self._store: OrderedDict[str, list[float]] = OrderedDict()

    def get(self, content: str) -> list[float] | None:
        """Retrieve a cached embedding by content.

        If the content is found, it is marked as recently used (moved to end).

        Args:
            content: The original text whose embedding was cached.

        Returns:
            The cached embedding vector, or ``None`` on a cache miss.
        """
        key = self._hash(content)
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, content: str, embedding: list[float]) -> None:
        """Store an embedding in the cache.

        If the cache is at capacity, the least-recently-used entry is evicted.

        Args:
            content: The original text.
            embedding: The embedding vector to cache.
        """
        key = self._hash(content)
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = embedding
        if len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def _hash(self, content: str) -> str:
        """Compute the SHA-256 hex digest of *content*.

        Args:
            content: Text to hash.

        Returns:
            Hex-encoded SHA-256 digest.
        """
        return hashlib.sha256(content.encode()).hexdigest()
