"""Common models shared across MCP tool domains."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class ErrorCode(StrEnum):
    """Standard error codes for MCP tool responses."""

    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DB_ERROR = "DB_ERROR"
    EMBEDDING_ERROR = "EMBEDDING_ERROR"


class ErrorResponse(BaseModel):
    """Structured error response returned by MCP tools.

    Attributes:
        error: Human-readable error message.
        code: Machine-readable error code from ErrorCode enum.
    """

    error: str
    code: ErrorCode
