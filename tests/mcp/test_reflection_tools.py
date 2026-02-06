"""Tests for reflection tool handlers.

Each tool function is tested for:
- Correct delegation to the underlying service
- Correct error handling (returns ErrorResponse on failure)
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


class TestInitReflectionTools:
    """Tests for init_reflection_tools() setup."""

    def test_init_reflection_tools_sets_service(self) -> None:
        """init_reflection_tools should set the module-level service global."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = object()
        ref_mod.init_reflection_tools(mock_svc)

        assert ref_mod._reflection_service is mock_svc


class TestReflect:
    """Tests for the reflect() tool function."""

    @pytest.mark.asyncio
    async def test_reflect_calls_service(self) -> None:
        """reflect() should forward all parameters to _reflection_service.reflect."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.reflect.return_value = {
            "what_went_wrong": "test",
            "root_cause": "test",
            "what_to_try_next": "test",
            "general_lesson": "test",
            "episode_id": "memory:ep1",
            "feedback_type": "test_failure",
        }

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            result = await ref_mod.reflect(
                output="failed output",
                feedback="AssertionError",
                feedback_type="test_failure",
                task="implement add",
                approach="brute force",
                model_used="haiku",
                code_context="def add(a, b): return a",
                file_path="src/math.py",
            )

        mock_svc.reflect.assert_awaited_once_with(
            output="failed output",
            feedback="AssertionError",
            feedback_type="test_failure",
            task="implement add",
            approach="brute force",
            model_used="haiku",
            code_context="def add(a, b): return a",
            file_path="src/math.py",
        )
        assert result["episode_id"] == "memory:ep1"

    @pytest.mark.asyncio
    async def test_reflect_returns_error_on_exception(self) -> None:
        """reflect() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.reflect.side_effect = RuntimeError("DB down")

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            result = await ref_mod.reflect(output="out", feedback="fb")

        assert "error" in result
        assert "DB down" in result["error"]

    @pytest.mark.asyncio
    async def test_reflect_passes_all_parameters(self) -> None:
        """reflect() should pass every parameter through to the service."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.reflect.return_value = {"episode_id": "memory:ep1"}

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            await ref_mod.reflect(
                output="out",
                feedback="fb",
                feedback_type="lint_failure",
                task="t",
                approach="a",
                model_used="opus",
                code_context="ctx",
                file_path="src/test.py",
            )

        call_kwargs = mock_svc.reflect.call_args[1]
        assert call_kwargs["feedback_type"] == "lint_failure"
        assert call_kwargs["model_used"] == "opus"
        assert call_kwargs["code_context"] == "ctx"
        assert call_kwargs["file_path"] == "src/test.py"


class TestImprovedAttempt:
    """Tests for the improved_attempt() tool function."""

    @pytest.mark.asyncio
    async def test_improved_attempt_calls_service(self) -> None:
        """improved_attempt() should forward parameters to service."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.improved_attempt.return_value = {
            "guidance": "Try X",
            "similar_episodes": [],
            "confidence": 0.0,
        }

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            result = await ref_mod.improved_attempt(
                task="fix parser",
                original_output="broken",
            )

        mock_svc.improved_attempt.assert_awaited_once_with(
            task="fix parser",
            original_output="broken",
            error_pattern="",
        )
        assert result["guidance"] == "Try X"

    @pytest.mark.asyncio
    async def test_improved_attempt_returns_error_on_exception(self) -> None:
        """improved_attempt() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.improved_attempt.side_effect = RuntimeError("Search failed")

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            result = await ref_mod.improved_attempt(
                task="task", original_output="out"
            )

        assert "error" in result
        assert "Search failed" in result["error"]

    @pytest.mark.asyncio
    async def test_improved_attempt_with_error_pattern(self) -> None:
        """improved_attempt() should pass error_pattern to service."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.improved_attempt.return_value = {
            "guidance": "Check types",
            "similar_episodes": [],
            "confidence": 0.5,
        }

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            await ref_mod.improved_attempt(
                task="fix bug",
                original_output="out",
                error_pattern="TypeError",
            )

        mock_svc.improved_attempt.assert_awaited_once_with(
            task="fix bug",
            original_output="out",
            error_pattern="TypeError",
        )


class TestModelEffectiveness:
    """Tests for the model_effectiveness() tool function."""

    @pytest.mark.asyncio
    async def test_model_effectiveness_calls_service(self) -> None:
        """model_effectiveness() should forward parameters to service."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.model_effectiveness.return_value = {
            "recommended_model": "haiku",
            "confidence": 0.8,
            "reasoning": "test",
            "stats": {},
        }

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            result = await ref_mod.model_effectiveness(
                task_pattern="code generation",
            )

        mock_svc.model_effectiveness.assert_awaited_once_with(
            task_pattern="code generation",
            feedback_type=None,
        )
        assert result["recommended_model"] == "haiku"

    @pytest.mark.asyncio
    async def test_model_effectiveness_returns_error_on_exception(self) -> None:
        """model_effectiveness() should return ErrorResponse when service raises."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.model_effectiveness.side_effect = RuntimeError("Query failed")

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            result = await ref_mod.model_effectiveness(task_pattern="test")

        assert "error" in result
        assert "Query failed" in result["error"]

    @pytest.mark.asyncio
    async def test_model_effectiveness_with_feedback_type(self) -> None:
        """model_effectiveness() should pass feedback_type to service."""
        from codeagent.mcp.tools import reflect as ref_mod

        mock_svc = AsyncMock()
        mock_svc.model_effectiveness.return_value = {
            "recommended_model": "opus",
            "confidence": 0.9,
            "reasoning": "test",
            "stats": {},
        }

        with patch.object(ref_mod, "_reflection_service", mock_svc):
            await ref_mod.model_effectiveness(
                task_pattern="code gen",
                feedback_type="test_failure",
            )

        mock_svc.model_effectiveness.assert_awaited_once_with(
            task_pattern="code gen",
            feedback_type="test_failure",
        )
