"""Pydantic models for the memory domain.

Covers the unified memory table which stores knowledge, episodes,
decisions, patterns, and code chunks with vector embeddings.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MemoryType(StrEnum):
    """Discriminator for memory record types.

    Each type stores different structured data in the flexible metadata field.
    See docs/surrealdb-schema-reference.md for per-type metadata schemas.
    """

    KNOWLEDGE = "knowledge"
    EPISODE = "episode"
    DECISION = "decision"
    PATTERN = "pattern"
    CODE_CHUNK = "code_chunk"


class Memory(BaseModel):
    """Full memory record as stored in SurrealDB.

    Attributes:
        memory_id: SurrealDB record ID (e.g. "memory:abc123"). None before persistence.
        type: Discriminator for the kind of memory.
        content: The main text content of the memory.
        title: Optional human-readable title.
        metadata: Flexible type-specific metadata object.
        embedding: Vector embedding (typically 1536-dim from text-embedding-3-small).
        tags: Freeform tags for filtering.
        project: Optional project name for scoping.
        confidence: Confidence score, 0.0-1.0. Defaults to 1.0.
        access_count: Number of times this memory has been accessed.
        last_accessed: Timestamp of last access.
        source_task: Optional reference to the originating task record.
        created_at: Timestamp of creation.
        updated_at: Timestamp of last update.
    """

    memory_id: str | None = Field(default=None, description="SurrealDB record ID")
    type: MemoryType
    content: str
    title: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    project: str | None = None
    confidence: float = 1.0
    access_count: int = 0
    last_accessed: datetime | None = None
    source_task: str | None = None
    created_at: datetime
    updated_at: datetime


class MemoryCreate(BaseModel):
    """Input model for creating a new memory record.

    Only requires content and type. All other fields have sensible defaults.
    The embedding is computed by the server, not provided by the caller.

    Attributes:
        content: The main text content of the memory.
        type: Discriminator for the kind of memory.
        title: Optional human-readable title.
        metadata: Optional type-specific metadata.
        tags: Optional freeform tags.
        project: Optional project name for scoping.
        confidence: Confidence score, defaults to 1.0.
        source_task: Optional reference to the originating task record ID.
    """

    content: str
    type: MemoryType
    title: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    project: str | None = None
    confidence: float = 1.0
    source_task: str | None = None


class MemoryUpdate(BaseModel):
    """Input model for updating an existing memory record.

    The memory_id is required to identify the record. All other fields are
    optional; only provided fields will be updated.

    Attributes:
        memory_id: SurrealDB record ID of the memory to update.
        content: New content text, if updating.
        title: New title, if updating.
        metadata: New metadata, if updating.
        tags: New tags, if updating.
        confidence: New confidence score, if updating.
    """

    memory_id: str
    content: str | None = None
    title: str | None = None
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None
    confidence: float | None = None


class SearchResult(BaseModel):
    """A single search hit in the index (lightweight).

    Attributes:
        id: SurrealDB record ID of the matching memory.
        title: Optional title of the matching memory.
        type: The memory type.
        score: Relevance score (higher is more relevant).
        snippet: A text snippet from the matching content.
    """

    id: str
    title: str | None
    type: MemoryType
    score: float
    snippet: str


class SearchResponse(BaseModel):
    """Response from a memory search operation.

    Contains both a lightweight index for quick scanning and full details
    for the matching memories.

    Attributes:
        index: List of lightweight search results.
        details: List of full Memory objects for the matches.
        total_count: Total number of matching results.
    """

    index: list[SearchResult]
    details: list[Memory]
    total_count: int
