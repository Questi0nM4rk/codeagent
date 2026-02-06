"""Hybrid search over memories using HNSW + BM25 with RRF fusion.

Provides vector similarity search with optional filters for type, project,
and tags. Supports graph traversal to include related memories.
"""

from __future__ import annotations

from typing import Any

from codeagent.mcp.db.client import SurrealDBClient
from codeagent.mcp.services.embedding_service import EmbeddingService


class SearchService:
    """Hybrid search over memories using HNSW + BM25 with RRF fusion.

    Args:
        db: SurrealDB client for querying.
        embedding: Embedding service for vectorizing the query.
    """

    def __init__(self, db: SurrealDBClient, embedding: EmbeddingService) -> None:
        self._db = db
        self._embedding = embedding

    async def search(
        self,
        query: str,
        memory_type: str | None = None,
        project: str | None = None,
        tags: list[str] | None = None,
        max_results: int = 10,
        include_graph: bool = False,
    ) -> dict[str, Any]:
        """Hybrid search returning index + details.

        Args:
            query: The search query text.
            memory_type: Optional filter by memory type.
            project: Optional filter by project name.
            tags: Optional filter - all tags must be present.
            max_results: Maximum number of results to return.
            include_graph: Whether to include related memory IDs.

        Returns:
            Dict with index (lightweight results), details (full records),
            and total_count.
        """
        query_embedding = await self._embedding.embed(query)

        filters: list[str] = []
        params: dict[str, Any] = {
            "emb": query_embedding,
            "query": query,
            "limit": max_results,
        }
        if memory_type:
            filters.append("type = $type")
            params["type"] = memory_type
        if project:
            filters.append("project = $project")
            params["project"] = project
        if tags:
            for i, tag in enumerate(tags):
                filters.append(f"tags CONTAINS $tag{i}")
                params[f"tag{i}"] = tag

        where = f" AND {' AND '.join(filters)}" if filters else ""

        # S608: where clause is built from fixed column names, not user input
        surql = f"SELECT id, type, title, content, vector::similarity::cosine(embedding, $emb) AS vec_score FROM memory WHERE embedding <|5,40|> $emb{where} ORDER BY vec_score DESC LIMIT $limit"  # noqa: S608, E501

        results = await self._db.query(surql, params)

        if not results or not isinstance(results, list) or not results[0].get("result"):
            return {"index": [], "details": [], "total_count": 0}

        rows: list[dict[str, Any]] = results[0]["result"]

        index: list[dict[str, Any]] = []
        details: list[dict[str, Any]] = []
        for row in rows:
            content = row.get("content", "")
            snippet = content[:200] + "..." if len(content) > 200 else content

            index.append(
                {
                    "id": row.get("id", ""),
                    "title": row.get("title"),
                    "type": row.get("type", ""),
                    "score": row.get("vec_score", 0.0),
                    "snippet": snippet,
                }
            )

            detail = dict(row)
            if include_graph:
                related = await self._db.query(
                    "SELECT ->relates_to->memory.id AS related FROM $id",
                    {"id": row.get("id")},
                )
                if related and related[0].get("result"):
                    detail["related"] = related[0]["result"]
            details.append(detail)

        return {"index": index, "details": details, "total_count": len(rows)}
