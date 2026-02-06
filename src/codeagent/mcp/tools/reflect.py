"""MCP tool handlers for reflection operations.

Each tool validates inputs, delegates to the ReflectionService,
and returns a dict response (or ErrorResponse dict on failure).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from codeagent.mcp.models import ErrorCode, ErrorResponse

if TYPE_CHECKING:
    from codeagent.mcp.services.reflection_service import ReflectionService

# Service instance, set by init_reflection_tools()
_reflection_service: ReflectionService | None = None


def init_reflection_tools(reflection_service: ReflectionService) -> None:
    """Initialize tool dependencies.

    Must be called before any tool function is invoked.

    Args:
        reflection_service: Service handling reflection, improved attempts,
            and model effectiveness queries.
    """
    global _reflection_service  # noqa: PLW0603
    _reflection_service = reflection_service


async def reflect(  # noqa: PLR0913
    output: str,
    feedback: str,
    feedback_type: str = "test_failure",
    task: str = "",
    approach: str = "",
    model_used: str | None = None,
    code_context: str = "",
    file_path: str | None = None,
) -> dict[str, Any]:
    """Analyze a failure and store a structured reflection as an episode.

    Args:
        output: The failed output or code.
        feedback: Error message or feedback describing the failure.
        feedback_type: Category of feedback (e.g. "test_failure", "lint_failure").
        task: Description of the task being attempted.
        approach: Description of the approach that was tried.
        model_used: Which model was used (e.g. "haiku", "opus").
        code_context: Surrounding code context.
        file_path: Path to the file being worked on.

    Returns:
        Dict with structured reflection and episode_id, or an error response.
    """
    if _reflection_service is None:
        return ErrorResponse(
            error="Reflection tools not initialized",
            code=ErrorCode.VALIDATION_ERROR,
        ).model_dump()
    try:
        return await _reflection_service.reflect(
            output=output,
            feedback=feedback,
            feedback_type=feedback_type,
            task=task,
            approach=approach,
            model_used=model_used,
            code_context=code_context,
            file_path=file_path,
        )
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def improved_attempt(
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
        Dict with guidance, similar episodes, and confidence, or an error response.
    """
    if _reflection_service is None:
        return ErrorResponse(
            error="Reflection tools not initialized",
            code=ErrorCode.VALIDATION_ERROR,
        ).model_dump()
    try:
        return await _reflection_service.improved_attempt(
            task=task,
            original_output=original_output,
            error_pattern=error_pattern,
        )
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()


async def model_effectiveness(
    task_pattern: str,
    feedback_type: str | None = None,
) -> dict[str, Any]:
    """Recommend which model to use based on historical episode data.

    Args:
        task_pattern: Pattern describing the type of task.
        feedback_type: Optional filter for a specific feedback type.

    Returns:
        Dict with recommended model, confidence, reasoning, and stats,
        or an error response.
    """
    if _reflection_service is None:
        return ErrorResponse(
            error="Reflection tools not initialized",
            code=ErrorCode.VALIDATION_ERROR,
        ).model_dump()
    try:
        return await _reflection_service.model_effectiveness(
            task_pattern=task_pattern,
            feedback_type=feedback_type,
        )
    except Exception as e:  # noqa: BLE001
        return ErrorResponse(error=str(e), code=ErrorCode.DB_ERROR).model_dump()
