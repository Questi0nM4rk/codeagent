"""Memory CRUD operations backed by SurrealDB.

Business logic for storing, reading, updating, deleting, linking, and
querying statistics for memory records. Handles embedding generation and
automatic graph linking on store.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from codeagent.mcp.db.client import SurrealDBClient
from codeagent.mcp.models.memory import MemoryCreate, MemoryUpdate
from codeagent.mcp.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class MemoryService:
    """Memory CRUD operations backed by SurrealDB.

    Args:
        db: SurrealDB client for persistence.
        embedding: Embedding service for vectorizing content.
    """

    def __init__(self, db: SurrealDBClient, embedding: EmbeddingService) -> None:
        self._db = db
        self._embedding = embedding

    async def store(self, create: MemoryCreate) -> dict[str, Any]:
        """Store a new memory. Embeds content, inserts into DB, auto-links.

        Args:
            create: The memory creation data.

        Returns:
            The created record dict from SurrealDB.
        """
        embedding = await self._embedding.embed(create.content)
        data = create.model_dump()
        data["embedding"] = embedding
        result = await self._db.create("memory", data)
        if isinstance(result, list):
            result = result[0]
        record_id = result.get("id", "")
        try:
            await self._auto_link(record_id, embedding)
        except Exception:  # noqa: BLE001 - auto-linking is best-effort
            logger.warning("Auto-link failed for %s; continuing", record_id)
        return result

    async def read(self, memory_id: str, depth: int = 1) -> dict[str, Any]:
        """Read a memory by ID with graph neighborhood.

        Args:
            memory_id: SurrealDB record ID (e.g. "memory:abc123").
            depth: Graph traversal depth. 0 means no related memories.

        Returns:
            The memory record dict, or an error dict if not found.
        """
        await self._db.query(
            "UPDATE $id SET access_count += 1, last_accessed = time::now()",
            {"id": memory_id},
        )
        result = await self._db.select(memory_id)
        if not result:
            return {"error": "Memory not found", "code": "NOT_FOUND"}
        if depth > 0:
            related = await self._db.query(
                "SELECT *, ->relates_to->memory.* AS out_links, "
                "<-relates_to<-memory.* AS in_links FROM $id",
                {"id": memory_id},
            )
            if related and isinstance(related, list) and related[0].get("result"):
                result["related_memories"] = related[0]["result"]
        return result

    async def update(self, update: MemoryUpdate) -> dict[str, Any]:
        """Update a memory. Re-embed if content changed.

        Args:
            update: The memory update data (memory_id required, other fields optional).

        Returns:
            The updated record dict from SurrealDB.
        """
        data = update.model_dump(exclude_none=True, exclude={"memory_id"})
        if "content" in data:
            data["embedding"] = await self._embedding.embed(data["content"])
        data["updated_at"] = datetime.now(UTC).isoformat()
        return await self._db.update(update.memory_id, data)

    async def delete(self, memory_id: str) -> dict[str, Any]:
        """Delete a memory (preserved in changefeed for audit).

        Args:
            memory_id: SurrealDB record ID to delete.

        Returns:
            Confirmation dict with deleted ID and DB result.
        """
        result = await self._db.delete(memory_id)
        return {"deleted": memory_id, "result": result}

    async def link(
        self,
        from_id: str,
        to_id: str,
        reason: str = "",
        strength: float = 0.8,
    ) -> dict[str, Any]:
        """Create a manual graph edge between two memories.

        Args:
            from_id: Source memory record ID.
            to_id: Target memory record ID.
            reason: Human-readable reason for the link.
            strength: Link strength from 0.0 to 1.0.

        Returns:
            Dict indicating success and the DB result.
        """
        result = await self._db.query(
            "RELATE $from->relates_to->$to SET "
            "strength = $strength, reason = $reason, auto = false",
            {"from": from_id, "to": to_id, "strength": strength, "reason": reason},
        )
        return {"linked": True, "result": result}

    async def stats(
        self,
        project: str | None = None,
        memory_type: str | None = None,
    ) -> dict[str, Any]:
        """Memory statistics, optionally filtered by project or type.

        Args:
            project: Optional project name filter.
            memory_type: Optional memory type filter.

        Returns:
            Dict with total count, counts by type, and counts by project.
        """
        filters: list[str] = []
        params: dict[str, Any] = {}
        if project:
            filters.append("project = $project")
            params["project"] = project
        if memory_type:
            filters.append("type = $type")
            params["type"] = memory_type
        where = f" WHERE {' AND '.join(filters)}" if filters else ""

        # S608: where clause is built from fixed column names, not user input
        total = await self._db.query(
            f"SELECT count() AS total FROM memory{where} GROUP ALL",  # noqa: S608
            params,
        )
        by_type = await self._db.query(
            f"SELECT type, count() AS count FROM memory{where} GROUP BY type",  # noqa: S608
            params,
        )
        by_project = await self._db.query(
            f"SELECT project, count() AS count FROM memory{where} GROUP BY project",  # noqa: S608
            params,
        )

        total_val = 0
        if total and isinstance(total, list) and total[0].get("result"):
            result_list = total[0]["result"]
            if result_list:
                total_val = result_list[0].get("total", 0)

        type_dict: dict[str, int] = {}
        if by_type and isinstance(by_type, list) and by_type[0].get("result"):
            type_dict = {r["type"]: r["count"] for r in by_type[0]["result"]}

        project_dict: dict[str, int] = {}
        if by_project and isinstance(by_project, list) and by_project[0].get("result"):
            project_dict = {r["project"]: r["count"] for r in by_project[0]["result"]}

        return {
            "total": total_val,
            "by_type": type_dict,
            "by_project": project_dict,
        }

    async def _auto_link(self, memory_id: str, embedding: list[float]) -> None:
        """Find top 5 similar memories and create relates_to edges.

        Args:
            memory_id: The newly created memory's record ID.
            embedding: The new memory's embedding vector.
        """
        similar = await self._db.query(
            "SELECT id, vector::similarity::cosine(embedding, $emb) AS score "
            "FROM memory "
            "WHERE id != $id "
            "ORDER BY score DESC LIMIT 5",
            {"emb": embedding, "id": memory_id},
        )
        if similar and isinstance(similar, list) and similar[0].get("result"):
            targets = [
                mem for mem in similar[0]["result"] if mem.get("score", 0) > 0.7
            ]
            if targets:
                # Batch all RELATE statements into a single multi-statement query
                statements: list[str] = []
                params: dict[str, Any] = {"from": memory_id}
                for idx, mem in enumerate(targets):
                    statements.append(
                        f"RELATE $from->relates_to->$to{idx} SET "
                        f"strength = $score{idx}, "
                        f"reason = 'auto-linked by similarity', "
                        f"auto = true"
                    )
                    params[f"to{idx}"] = mem["id"]
                    params[f"score{idx}"] = mem["score"]
                await self._db.query("; ".join(statements), params)
