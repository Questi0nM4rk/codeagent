"""Structured failure analysis and learning from past episodes.

Provides reflection on failures, guidance from past episodes, and
model effectiveness recommendations based on historical episode data.
All episodes are stored as 'episode' type memories in the unified memory table.
"""

from __future__ import annotations

from typing import Any

from codeagent.mcp.db.client import SurrealDBClient
from codeagent.mcp.services.embedding_service import EmbeddingService


class ReflectionService:
    """Structured failure analysis and learning from past episodes.

    Args:
        db: SurrealDB client for persistence.
        embedding: Embedding service for vectorizing content.
    """

    def __init__(self, db: SurrealDBClient, embedding: EmbeddingService) -> None:
        self._db = db
        self._embedding = embedding

    async def reflect(
        self,
        output: str,
        feedback: str,
        feedback_type: str = "test_failure",
        task: str = "",
        approach: str = "",
        model_used: str | None = None,
        code_context: str = "",
        file_path: str | None = None,
        outcome: str = "failure",
    ) -> dict[str, Any]:
        """Analyze a failure, generate structured reflection, store as episode memory.

        Args:
            output: The failed output or code.
            feedback: Error message or feedback describing the failure.
            feedback_type: Category of feedback (e.g. "test_failure", "lint_failure").
            task: Description of the task being attempted.
            approach: Description of the approach that was tried.
            model_used: Which model was used (e.g. "haiku", "opus").
            code_context: Surrounding code context.
            file_path: Path to the file being worked on.
            outcome: Episode outcome (e.g. "failure", "success"). Defaults to "failure".

        Returns:
            Dict with: what_went_wrong, root_cause, what_to_try_next,
            general_lesson, episode_id, feedback_type.
        """
        reflection = {
            "what_went_wrong": f"Output failed: {feedback[:200]}",
            "root_cause": f"Approach: {approach}. Feedback type: {feedback_type}",
            "what_to_try_next": f"Review the {feedback_type} and adjust approach",
            "general_lesson": f"When encountering {feedback_type}, verify assumptions first",
        }

        content = (
            f"Task: {task}\nApproach: {approach}\nFeedback: {feedback}\nOutput: {output[:500]}"
        )
        if code_context:
            content += f"\nContext: {code_context[:500]}"
        metadata: dict[str, Any] = {
            "outcome": outcome,
            "feedback_type": feedback_type,
            "model_used": model_used,
            "file_path": file_path,
            "reflection": reflection,
        }

        tags = [f"feedback:{feedback_type}"]
        if model_used:
            tags.append(f"model:{model_used}")

        embedding = await self._embedding.embed(content)
        # Bypass MemoryService.store() intentionally: episodes use a fixed
        # schema and don't need Zettelkasten auto-linking on creation.
        result = await self._db.create(
            "memory",
            {
                "type": "episode",
                "content": content,
                "title": f"Episode: {task[:80]}" if task else f"Episode: {feedback_type}",
                "metadata": metadata,
                "embedding": embedding,
                "tags": tags,
                "confidence": 1.0,
            },
        )

        episode_id = result[0].get("id", "") if isinstance(result, list) else result.get("id", "")

        return {
            **reflection,
            "episode_id": episode_id,
            "feedback_type": feedback_type,
        }

    async def improved_attempt(
        self,
        task: str,
        original_output: str,
        error_pattern: str = "",
    ) -> dict[str, Any]:
        """Query past failures and generate guidance for a new attempt.

        Args:
            task: Description of the current task.
            original_output: The output from the failed attempt.
            error_pattern: Optional error pattern to search for.

        Returns:
            Dict with: guidance, similar_episodes, confidence.
        """
        query = f"{task} {error_pattern} {original_output[:200]}".strip()
        embedding = await self._embedding.embed(query)

        result = await self._db.query(
            """SELECT *, vector::similarity::cosine(embedding, $emb) AS score
               FROM memory
               WHERE type = 'episode'
               ORDER BY score DESC LIMIT 5""",
            {"emb": embedding},
        )

        episodes: list[dict[str, Any]] = []
        if result and isinstance(result, list) and result[0].get("result"):
            episodes = result[0]["result"]

        if not episodes:
            return {
                "guidance": "No similar past episodes found. Try a fresh approach.",
                "similar_episodes": [],
                "confidence": 0.0,
            }

        lessons: list[dict[str, Any]] = []
        for ep in episodes:
            meta = ep.get("metadata", {})
            reflection = meta.get("reflection", {})
            if reflection:
                lessons.append(
                    {
                        "episode_id": ep.get("id", ""),
                        "score": ep.get("score", 0),
                        "lesson": reflection.get("general_lesson", ""),
                        "what_to_try": reflection.get("what_to_try_next", ""),
                    }
                )

        lesson_texts = "; ".join(le["lesson"] for le in lessons[:3] if le["lesson"])
        return {
            "guidance": f"Found {len(episodes)} similar episodes. Key lessons: {lesson_texts}",
            "similar_episodes": lessons,
            "confidence": episodes[0].get("score", 0) if episodes else 0.0,
        }

    async def model_effectiveness(
        self,
        task_pattern: str,
        feedback_type: str | None = None,
    ) -> dict[str, Any]:
        """Recommend which model to use based on historical episode data.

        Args:
            task_pattern: Pattern describing the type of task.
            feedback_type: Optional filter for a specific feedback type.

        Returns:
            Dict with: recommended_model, confidence, reasoning, stats.
        """
        filters = ["type = 'episode'"]
        params: dict[str, Any] = {}
        if task_pattern:
            filters.append("content CONTAINS $pattern")
            params["pattern"] = task_pattern
        if feedback_type:
            filters.append("metadata.feedback_type = $ftype")
            params["ftype"] = feedback_type

        where = " AND ".join(filters)

        # S608: where clause is built from fixed column names, not user input
        result = await self._db.query(
            f"SELECT metadata.model_used AS model, metadata.outcome AS outcome "  # noqa: S608
            f"FROM memory WHERE {where}",
            params,
        )

        if not result or not isinstance(result, list) or not result[0].get("result"):
            return {
                "recommended_model": "sonnet",
                "confidence": 0.0,
                "reasoning": "No historical data available. Defaulting to sonnet.",
                "stats": {},
            }

        rows = result[0]["result"]

        model_stats: dict[str, dict[str, int]] = {}
        for row in rows:
            model = row.get("model") or "unknown"
            outcome = row.get("outcome", "unknown")
            if model not in model_stats:
                model_stats[model] = {"success": 0, "failure": 0, "total": 0}
            model_stats[model]["total"] += 1
            if outcome == "success":
                model_stats[model]["success"] += 1
            else:
                model_stats[model]["failure"] += 1

        best_model = "sonnet"
        best_rate = 0.0
        for model, stats in model_stats.items():
            if model == "unknown":
                continue
            rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            if rate > best_rate or (
                rate == best_rate
                and rate > 0
                and stats["total"] > model_stats.get(best_model, {}).get("total", 0)
            ):
                best_rate = rate
                best_model = model

        total_episodes = sum(s["total"] for s in model_stats.values())
        return {
            "recommended_model": best_model,
            "confidence": best_rate,
            "reasoning": (
                f"Based on {total_episodes} episodes. "
                f"{best_model} has {best_rate:.0%} success rate."
            ),
            "stats": model_stats,
        }
