"""Tests for common models (ErrorResponse, ErrorCode)."""

from __future__ import annotations

import pytest


class TestErrorCode:
    """Tests for the ErrorCode enum."""

    def test_error_code_has_not_found(self) -> None:
        """ErrorCode must include NOT_FOUND."""
        from codeagent.mcp.models.common import ErrorCode

        assert ErrorCode.NOT_FOUND == "NOT_FOUND"

    def test_error_code_has_validation_error(self) -> None:
        """ErrorCode must include VALIDATION_ERROR."""
        from codeagent.mcp.models.common import ErrorCode

        assert ErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"

    def test_error_code_has_db_error(self) -> None:
        """ErrorCode must include DB_ERROR."""
        from codeagent.mcp.models.common import ErrorCode

        assert ErrorCode.DB_ERROR == "DB_ERROR"

    def test_error_code_has_embedding_error(self) -> None:
        """ErrorCode must include EMBEDDING_ERROR."""
        from codeagent.mcp.models.common import ErrorCode

        assert ErrorCode.EMBEDDING_ERROR == "EMBEDDING_ERROR"

    def test_error_code_is_str_enum(self) -> None:
        """ErrorCode values should be usable as strings."""
        from codeagent.mcp.models.common import ErrorCode

        code = ErrorCode.NOT_FOUND
        assert isinstance(code, str)
        assert code == "NOT_FOUND"


class TestErrorResponse:
    """Tests for the ErrorResponse model."""

    def test_create_error_response(self) -> None:
        """ErrorResponse should hold an error message and code."""
        from codeagent.mcp.models.common import ErrorCode, ErrorResponse

        resp = ErrorResponse(error="User not found", code=ErrorCode.NOT_FOUND)
        assert resp.error == "User not found"
        assert resp.code == ErrorCode.NOT_FOUND

    def test_error_response_serializes_to_dict(self) -> None:
        """ErrorResponse should serialize to a dict."""
        from codeagent.mcp.models.common import ErrorCode, ErrorResponse

        resp = ErrorResponse(error="DB failure", code=ErrorCode.DB_ERROR)
        data = resp.model_dump()
        assert data["error"] == "DB failure"
        assert data["code"] == "DB_ERROR"

    def test_error_response_requires_error_field(self) -> None:
        """ErrorResponse should require the error field."""
        from pydantic import ValidationError

        from codeagent.mcp.models.common import ErrorCode, ErrorResponse

        with pytest.raises(ValidationError):
            ErrorResponse(code=ErrorCode.NOT_FOUND)  # type: ignore[call-arg]

    def test_error_response_requires_code_field(self) -> None:
        """ErrorResponse should require the code field."""
        from pydantic import ValidationError

        from codeagent.mcp.models.common import ErrorResponse

        with pytest.raises(ValidationError):
            ErrorResponse(error="Missing code")  # type: ignore[call-arg]

    def test_error_response_rejects_invalid_code(self) -> None:
        """ErrorResponse should reject a code string that is not in ErrorCode."""
        from pydantic import ValidationError

        from codeagent.mcp.models.common import ErrorResponse

        with pytest.raises(ValidationError):
            ErrorResponse(error="Bad code", code="INVALID_CODE")  # type: ignore[arg-type]
