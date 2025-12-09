"""
Self-Reflection MCP Server

Implements Reflexion pattern with episodic memory.
Based on NeurIPS 2023 research showing 67% → 88% improvement on HumanEval (+21%).

Tools:
- reflect_on_failure: Analyze why output failed and generate insights
- store_episode: Store a learning episode in memory
- retrieve_episodes: Find similar past episodes for learning
- generate_improved_attempt: Generate improved solution using reflection
- get_reflection_history: View reflection history for a task
- clear_episodes: Clear episodic memory
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "reflection",
    instructions="Self-reflection and episodic memory for learning from failures. "
    "Use this when code fails tests or reviews to improve on subsequent attempts.",
)


class FeedbackType(str, Enum):
    """Types of feedback that trigger reflection."""

    TEST_FAILURE = "test_failure"
    LINT_ERROR = "lint_error"
    BUILD_ERROR = "build_error"
    REVIEW_COMMENT = "review_comment"
    RUNTIME_ERROR = "runtime_error"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    TYPE_ERROR = "type_error"


class OutcomeType(str, Enum):
    """Outcome of an episode."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


@dataclass
class Reflection:
    """A reflection on a failure."""

    id: str
    what_went_wrong: str
    root_cause: str
    what_to_try_next: str
    general_lesson: str
    confidence: float  # 0-1 confidence in the reflection
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Episode:
    """An episodic memory of a task attempt."""

    id: str
    task: str
    approach: str
    outcome: OutcomeType
    feedback: str
    feedback_type: FeedbackType
    reflection: Reflection | None
    code_context: str  # Relevant code snippet
    file_path: str | None
    attempt_number: int
    duration_seconds: float | None
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# In-memory episodic storage
_episodes: list[Episode] = []
_task_attempts: dict[str, int] = {}  # Track attempt count per task


def _get_attempt_number(task: str) -> int:
    """Get and increment attempt number for a task."""
    key = task[:100]  # Normalize task key
    count = _task_attempts.get(key, 0) + 1
    _task_attempts[key] = count
    return count


def _keyword_similarity(text1: str, text2: str) -> float:
    """Simple keyword-based similarity score."""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # Remove common words
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                 'should', 'may', 'might', 'must', 'shall', 'can', 'to', 'of', 'in',
                 'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through',
                 'and', 'but', 'or', 'nor', 'so', 'yet', 'both', 'either', 'neither',
                 'not', 'only', 'own', 'same', 'than', 'too', 'very', 'just', 'that',
                 'this', 'these', 'those', 'it', 'its'}

    words1 = words1 - stopwords
    words2 = words2 - stopwords

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union) if union else 0.0


@mcp.tool()
def reflect_on_failure(
    output: str,
    feedback: str,
    feedback_type: str = "test_failure",
    context: str = "",
) -> dict[str, Any]:
    """
    Generate a structured reflection on why output failed.

    Args:
        output: The code or output that failed (can be truncated)
        feedback: The error message or feedback received
        feedback_type: Type of feedback (test_failure, lint_error, build_error, etc.)
        context: Additional context about what was being attempted

    Returns:
        Structured reflection with insights for improvement
    """
    reflection_id = str(uuid4())[:8]

    # Parse feedback type
    try:
        fb_type = FeedbackType(feedback_type)
    except ValueError:
        fb_type = FeedbackType.TEST_FAILURE

    # Generate reflection structure
    # In a production system, this would use an LLM to generate better reflections
    # Here we provide structured prompts for the calling agent to fill in

    return {
        "reflection_id": reflection_id,
        "output_summary": output[:500] if len(output) > 500 else output,
        "feedback": feedback,
        "feedback_type": fb_type.value,
        "context": context,
        "reflection_template": {
            "what_went_wrong": "[Describe the specific failure - what didn't work as expected]",
            "root_cause": "[Identify the underlying cause - why did this approach fail]",
            "what_to_try_next": "[Concrete next steps - what specific changes should be made]",
            "general_lesson": "[Broader lesson - what principle or pattern should be remembered]",
            "confidence": "[0.0-1.0 - how confident are you in this analysis]",
        },
        "guidance": {
            "test_failure": "Focus on what assertion failed and why the code doesn't satisfy the test condition.",
            "lint_error": "Identify the specific rule violation and the correct pattern to use.",
            "build_error": "Focus on type mismatches, missing imports, or syntax issues.",
            "review_comment": "Consider the reviewer's perspective and what they're trying to improve.",
            "runtime_error": "Focus on the error type and what state led to the failure.",
            "security_issue": "Identify the vulnerability class and secure alternatives.",
            "performance_issue": "Identify the bottleneck and more efficient approaches.",
            "type_error": "Focus on type mismatches and correct type annotations.",
        }.get(fb_type.value, "Analyze the failure systematically."),
        "instruction": "Complete the reflection_template with specific insights. "
        "Then call store_episode to save this for future learning.",
    }


@mcp.tool()
def store_episode(
    task: str,
    approach: str,
    outcome: str,
    feedback: str,
    feedback_type: str,
    reflection: dict[str, Any],
    code_context: str = "",
    file_path: str | None = None,
    tags: list[str] | None = None,
    duration_seconds: float | None = None,
) -> dict[str, Any]:
    """
    Store a learning episode in episodic memory.

    Args:
        task: Description of the task being attempted
        approach: The approach that was tried
        outcome: Result - 'success', 'partial', or 'failure'
        feedback: The feedback or error message
        feedback_type: Type of feedback
        reflection: Reflection dict with what_went_wrong, root_cause, what_to_try_next, general_lesson
        code_context: Relevant code snippet (truncated if needed)
        file_path: Path to the file being modified
        tags: Optional tags for categorization
        duration_seconds: How long the attempt took

    Returns:
        Stored episode ID and confirmation
    """
    episode_id = str(uuid4())[:8]

    # Parse outcome
    try:
        outcome_type = OutcomeType(outcome)
    except ValueError:
        outcome_type = OutcomeType.FAILURE

    # Parse feedback type
    try:
        fb_type = FeedbackType(feedback_type)
    except ValueError:
        fb_type = FeedbackType.TEST_FAILURE

    # Create reflection object
    refl = Reflection(
        id=str(uuid4())[:8],
        what_went_wrong=reflection.get("what_went_wrong", ""),
        root_cause=reflection.get("root_cause", ""),
        what_to_try_next=reflection.get("what_to_try_next", ""),
        general_lesson=reflection.get("general_lesson", ""),
        confidence=float(reflection.get("confidence", 0.5)),
    )

    # Create episode
    episode = Episode(
        id=episode_id,
        task=task,
        approach=approach,
        outcome=outcome_type,
        feedback=feedback[:2000],  # Truncate long feedback
        feedback_type=fb_type,
        reflection=refl,
        code_context=code_context[:3000],  # Truncate long code
        file_path=file_path,
        attempt_number=_get_attempt_number(task),
        duration_seconds=duration_seconds,
        tags=tags or [],
    )

    _episodes.append(episode)

    return {
        "episode_id": episode_id,
        "task": task[:100],
        "attempt_number": episode.attempt_number,
        "outcome": outcome_type.value,
        "stored": True,
        "total_episodes": len(_episodes),
        "lesson": refl.general_lesson,
    }


@mcp.tool()
def retrieve_episodes(
    task: str,
    error_pattern: str = "",
    feedback_type: str | None = None,
    top_k: int = 5,
    include_successes: bool = True,
) -> dict[str, Any]:
    """
    Retrieve similar past episodes for learning.

    Args:
        task: Current task description
        error_pattern: Optional error message to match
        feedback_type: Filter by feedback type
        top_k: Maximum episodes to return
        include_successes: Whether to include successful episodes

    Returns:
        Relevant past episodes with their reflections
    """
    top_k = min(max(top_k, 1), 20)

    # Filter episodes
    candidates = _episodes.copy()

    if feedback_type:
        try:
            fb_type = FeedbackType(feedback_type)
            candidates = [e for e in candidates if e.feedback_type == fb_type]
        except ValueError:
            pass

    if not include_successes:
        candidates = [e for e in candidates if e.outcome != OutcomeType.SUCCESS]

    # Score by similarity
    scored = []
    for episode in candidates:
        task_sim = _keyword_similarity(task, episode.task)
        error_sim = _keyword_similarity(error_pattern, episode.feedback) if error_pattern else 0

        # Combine scores (task similarity more important)
        score = task_sim * 0.7 + error_sim * 0.3

        # Boost recent episodes slightly
        scored.append((score, episode))

    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)

    # Take top-k
    results = []
    for score, episode in scored[:top_k]:
        results.append({
            "episode_id": episode.id,
            "task": episode.task[:200],
            "approach": episode.approach[:200],
            "outcome": episode.outcome.value,
            "feedback_type": episode.feedback_type.value,
            "attempt_number": episode.attempt_number,
            "similarity_score": round(score, 3),
            "reflection": {
                "what_went_wrong": episode.reflection.what_went_wrong if episode.reflection else "",
                "root_cause": episode.reflection.root_cause if episode.reflection else "",
                "what_to_try_next": episode.reflection.what_to_try_next if episode.reflection else "",
                "general_lesson": episode.reflection.general_lesson if episode.reflection else "",
            } if episode.reflection else None,
            "created_at": episode.created_at,
        })

    return {
        "query_task": task[:100],
        "query_error": error_pattern[:100] if error_pattern else None,
        "episodes": results,
        "count": len(results),
        "instruction": "Apply lessons from these past episodes to your current approach. "
        "Focus on the general_lesson and what_to_try_next fields.",
    }


@mcp.tool()
def generate_improved_attempt(
    original_output: str,
    reflection: dict[str, Any],
    similar_episodes: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Generate guidance for an improved attempt based on reflection and past lessons.

    Args:
        original_output: The code/output that failed
        reflection: Current reflection (from reflect_on_failure)
        similar_episodes: Past episodes to learn from (from retrieve_episodes)

    Returns:
        Guidance for generating an improved solution
    """
    # Extract lessons from episodes
    past_lessons = []
    if similar_episodes:
        for ep in similar_episodes:
            if ep.get("reflection") and ep["reflection"].get("general_lesson"):
                past_lessons.append({
                    "task": ep.get("task", "")[:80],
                    "lesson": ep["reflection"]["general_lesson"],
                    "what_worked": ep["reflection"].get("what_to_try_next", ""),
                })

    return {
        "original_output_summary": original_output[:300],
        "current_reflection": {
            "root_cause": reflection.get("root_cause", "Unknown"),
            "what_to_try_next": reflection.get("what_to_try_next", ""),
        },
        "past_lessons": past_lessons[:5],  # Top 5 relevant lessons
        "improvement_strategy": {
            "1_address_root_cause": f"Fix: {reflection.get('root_cause', 'the identified issue')}",
            "2_apply_lesson": reflection.get("what_to_try_next", "Apply the learned approach"),
            "3_avoid_patterns": "Don't repeat approaches that failed in similar past episodes",
            "4_verify_before_submit": "Ensure the fix addresses the original feedback",
        },
        "instruction": "Generate improved code that: "
        "1) Addresses the root cause identified in reflection, "
        "2) Applies lessons from similar past episodes, "
        "3) Avoids patterns that led to failures before. "
        "Focus on correctness over cleverness.",
    }


@mcp.tool()
def get_reflection_history(
    task: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    View reflection history, optionally filtered by task.

    Args:
        task: Optional task to filter by (substring match)
        limit: Maximum entries to return

    Returns:
        History of reflections with outcomes
    """
    limit = min(max(limit, 1), 50)

    # Filter episodes
    if task:
        filtered = [e for e in _episodes if task.lower() in e.task.lower()]
    else:
        filtered = _episodes.copy()

    # Sort by created_at descending (most recent first)
    filtered.sort(key=lambda e: e.created_at, reverse=True)

    # Format results
    history = []
    for episode in filtered[:limit]:
        history.append({
            "episode_id": episode.id,
            "task": episode.task[:100],
            "outcome": episode.outcome.value,
            "feedback_type": episode.feedback_type.value,
            "attempt_number": episode.attempt_number,
            "lesson": episode.reflection.general_lesson if episode.reflection else None,
            "created_at": episode.created_at,
        })

    # Calculate stats
    outcomes = [e.outcome for e in filtered]
    stats = {
        "total": len(filtered),
        "successes": sum(1 for o in outcomes if o == OutcomeType.SUCCESS),
        "partial": sum(1 for o in outcomes if o == OutcomeType.PARTIAL),
        "failures": sum(1 for o in outcomes if o == OutcomeType.FAILURE),
    }

    return {
        "history": history,
        "stats": stats,
        "filter": task,
    }


@mcp.tool()
def get_common_lessons() -> dict[str, Any]:
    """
    Get aggregated lessons from all episodes, grouped by feedback type.

    Returns:
        Common lessons learned, organized by feedback type
    """
    lessons_by_type: dict[str, list[str]] = {}

    for episode in _episodes:
        if episode.reflection and episode.reflection.general_lesson:
            fb_type = episode.feedback_type.value
            if fb_type not in lessons_by_type:
                lessons_by_type[fb_type] = []
            lessons_by_type[fb_type].append(episode.reflection.general_lesson)

    # Deduplicate and format
    formatted = {}
    for fb_type, lessons in lessons_by_type.items():
        # Simple deduplication by keeping unique lessons
        unique = list(set(lessons))
        formatted[fb_type] = unique[:10]  # Top 10 per type

    return {
        "lessons_by_feedback_type": formatted,
        "total_episodes": len(_episodes),
        "instruction": "Use these accumulated lessons to avoid repeating past mistakes.",
    }


@mcp.tool()
def clear_episodes(
    older_than_days: int | None = None,
    feedback_type: str | None = None,
) -> dict[str, Any]:
    """
    Clear episodic memory, optionally with filters.

    Args:
        older_than_days: Only clear episodes older than N days
        feedback_type: Only clear episodes of this feedback type

    Returns:
        Number of episodes cleared
    """
    global _episodes

    initial_count = len(_episodes)

    if older_than_days is None and feedback_type is None:
        # Clear all
        _episodes = []
        _task_attempts.clear()
        return {"cleared": initial_count, "remaining": 0}

    # Filter what to keep
    keep = []
    now = datetime.now()

    for episode in _episodes:
        should_remove = True

        if older_than_days is not None:
            episode_time = datetime.fromisoformat(episode.created_at)
            age_days = (now - episode_time).days
            if age_days < older_than_days:
                should_remove = False

        if feedback_type is not None:
            try:
                fb_type = FeedbackType(feedback_type)
                if episode.feedback_type != fb_type:
                    should_remove = False
            except ValueError:
                pass

        if not should_remove:
            keep.append(episode)

    cleared = initial_count - len(keep)
    _episodes = keep

    return {"cleared": cleared, "remaining": len(_episodes)}


@mcp.tool()
def get_episode_stats() -> dict[str, Any]:
    """
    Get statistics about episodic memory.

    Returns:
        Statistics including counts, success rates, common failure types
    """
    if not _episodes:
        return {"message": "No episodes stored yet.", "total": 0}

    # Count by outcome
    outcomes = {}
    for outcome in OutcomeType:
        outcomes[outcome.value] = sum(1 for e in _episodes if e.outcome == outcome)

    # Count by feedback type
    feedback_types = {}
    for fb_type in FeedbackType:
        count = sum(1 for e in _episodes if e.feedback_type == fb_type)
        if count > 0:
            feedback_types[fb_type.value] = count

    # Calculate success rate
    total = len(_episodes)
    success_rate = outcomes.get("success", 0) / total if total > 0 else 0

    # Average attempts per task
    avg_attempts = sum(e.attempt_number for e in _episodes) / total if total > 0 else 0

    # Most common failure types (for failures only)
    failure_types = {}
    for e in _episodes:
        if e.outcome == OutcomeType.FAILURE:
            fb = e.feedback_type.value
            failure_types[fb] = failure_types.get(fb, 0) + 1

    return {
        "total_episodes": total,
        "by_outcome": outcomes,
        "by_feedback_type": feedback_types,
        "success_rate": round(success_rate, 3),
        "average_attempts": round(avg_attempts, 2),
        "most_common_failures": dict(sorted(failure_types.items(), key=lambda x: x[1], reverse=True)[:5]),
    }


def main():
    """Entry point for the reflection MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
