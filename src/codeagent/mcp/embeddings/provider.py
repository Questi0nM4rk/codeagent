"""Async embedding provider using OpenAI's text-embedding-3-small model."""

from __future__ import annotations

import os

import httpx


class EmbeddingProvider:
    """Generates embeddings using OpenAI's text-embedding-3-small model.

    Uses raw httpx calls to the OpenAI API to avoid the heavy ``openai`` package
    dependency. Embeddings are 1536-dimensional float vectors.

    Example::

        provider = EmbeddingProvider(api_key="sk-...")
        vector = await provider.embed("hello world")
    """

    MODEL = "text-embedding-3-small"
    DIMENSIONS = 1536

    _API_URL = "https://api.openai.com/v1/embeddings"

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the provider.

        Args:
            api_key: OpenAI API key. Falls back to the ``OPENAI_API_KEY``
                environment variable when not provided.

        Raises:
            ValueError: If no API key is available from either argument or env.
        """
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            msg = (
                "OpenAI API key is required. "
                "Pass api_key or set the OPENAI_API_KEY environment variable."
            )
            raise ValueError(msg)
        self._api_key: str = resolved_key

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            A list of floats representing the embedding vector.

        Raises:
            httpx.HTTPStatusError: If the OpenAI API returns a non-2xx status.
        """
        results = await self._request([text])
        return results[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in a single API call.

        Args:
            texts: The texts to embed.

        Returns:
            A list of embedding vectors, one per input text, in the same order
            as the input.

        Raises:
            httpx.HTTPStatusError: If the OpenAI API returns a non-2xx status.
        """
        return await self._request(texts)

    async def _request(self, texts: list[str]) -> list[list[float]]:
        """Send an embedding request to the OpenAI API.

        Args:
            texts: Texts to embed.

        Returns:
            Embedding vectors sorted by the ``index`` field in the API response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._API_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": texts,
                    "model": self.MODEL,
                    "dimensions": self.DIMENSIONS,
                },
            )
            response.raise_for_status()

        data = response.json()["data"]
        sorted_data = sorted(data, key=lambda item: item["index"])
        return [item["embedding"] for item in sorted_data]
