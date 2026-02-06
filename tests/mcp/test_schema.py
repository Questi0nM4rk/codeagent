"""Tests for the SurrealDB schema file content.

These tests verify the schema.surql file contains all required definitions
without needing a running SurrealDB instance.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).parents[2] / "src" / "codeagent" / "mcp" / "db" / "schema.surql"


@pytest.fixture
def schema_content() -> str:
    """Load the schema file content."""
    return SCHEMA_PATH.read_text()


class TestSchemaFileExists:
    """Verify the schema file exists and is non-empty."""

    def test_schema_file_exists(self) -> None:
        """The schema.surql file should exist."""
        assert SCHEMA_PATH.exists(), f"Schema file not found at {SCHEMA_PATH}"

    def test_schema_file_not_empty(self, schema_content: str) -> None:
        """The schema file should not be empty."""
        assert len(schema_content.strip()) > 0


class TestAnalyzerDefinition:
    """Verify the custom analyzer is defined."""

    def test_defines_memory_analyzer(self, schema_content: str) -> None:
        """Schema should define the memory_analyzer."""
        assert "DEFINE ANALYZER memory_analyzer" in schema_content

    def test_analyzer_uses_snowball_english(self, schema_content: str) -> None:
        """Analyzer should use snowball(english) filter."""
        assert "snowball(english)" in schema_content

    def test_analyzer_uses_blank_tokenizer(self, schema_content: str) -> None:
        """Analyzer should use blank tokenizer."""
        assert "TOKENIZERS blank" in schema_content

    def test_analyzer_uses_camel_tokenizer(self, schema_content: str) -> None:
        """Analyzer should use camel tokenizer."""
        assert "TOKENIZERS blank, class, camel" in schema_content


class TestMemoryTable:
    """Verify the memory table definition."""

    def test_defines_memory_table(self, schema_content: str) -> None:
        """Schema should define the memory table as SCHEMAFULL with CHANGEFEED."""
        assert "DEFINE TABLE memory SCHEMAFULL CHANGEFEED 90d" in schema_content

    def test_memory_has_type_field(self, schema_content: str) -> None:
        """Memory table should have a type field with ASSERT constraint."""
        assert "DEFINE FIELD type ON memory TYPE string" in schema_content
        assert '"knowledge"' in schema_content
        assert '"episode"' in schema_content
        assert '"decision"' in schema_content
        assert '"pattern"' in schema_content
        assert '"code_chunk"' in schema_content

    def test_memory_has_content_field(self, schema_content: str) -> None:
        """Memory table should have a content field."""
        assert "DEFINE FIELD content ON memory TYPE string" in schema_content

    def test_memory_has_embedding_field(self, schema_content: str) -> None:
        """Memory table should have an embedding field."""
        assert "DEFINE FIELD embedding ON memory TYPE array<float>" in schema_content

    def test_memory_has_tags_field(self, schema_content: str) -> None:
        """Memory table should have a tags field with default."""
        assert "DEFINE FIELD tags ON memory TYPE array<string>" in schema_content

    def test_memory_has_project_field(self, schema_content: str) -> None:
        """Memory table should have an optional project field."""
        assert "DEFINE FIELD project ON memory TYPE option<string>" in schema_content

    def test_memory_has_confidence_field(self, schema_content: str) -> None:
        """Memory table should have a confidence field with default."""
        assert "DEFINE FIELD confidence ON memory TYPE float DEFAULT 1.0" in schema_content

    def test_memory_has_access_count_field(self, schema_content: str) -> None:
        """Memory table should have an access_count field."""
        assert "DEFINE FIELD access_count ON memory TYPE int DEFAULT 0" in schema_content

    def test_memory_has_source_task_field(self, schema_content: str) -> None:
        """Memory table should have an optional source_task record reference."""
        assert "DEFINE FIELD source_task ON memory TYPE option<record<task>>" in schema_content

    def test_memory_has_timestamps(self, schema_content: str) -> None:
        """Memory table should have created_at and updated_at timestamps."""
        created = "DEFINE FIELD created_at ON memory TYPE datetime DEFAULT time::now()"
        updated = "DEFINE FIELD updated_at ON memory TYPE datetime DEFAULT time::now()"
        assert created in schema_content
        assert updated in schema_content


class TestMemoryIndexes:
    """Verify memory table indexes."""

    def test_hnsw_vector_index(self, schema_content: str) -> None:
        """Memory should have an HNSW vector index with correct parameters."""
        assert "HNSW DIMENSION 1536 DIST COSINE TYPE F32 EFC 200 M 16" in schema_content

    def test_full_text_index(self, schema_content: str) -> None:
        """Memory should have a BM25 full-text index using memory_analyzer."""
        assert "memory_analyzer BM25" in schema_content

    def test_type_index(self, schema_content: str) -> None:
        """Memory should have an index on type."""
        assert "DEFINE INDEX memory_type ON memory FIELDS type" in schema_content

    def test_project_index(self, schema_content: str) -> None:
        """Memory should have an index on project."""
        assert "DEFINE INDEX memory_project ON memory FIELDS project" in schema_content

    def test_tags_index(self, schema_content: str) -> None:
        """Memory should have an index on tags."""
        assert "DEFINE INDEX memory_tags ON memory FIELDS tags" in schema_content


class TestRelatesToTable:
    """Verify the relates_to relation table."""

    def test_defines_relates_to_as_relation(self, schema_content: str) -> None:
        """Schema should define relates_to as a RELATION table."""
        assert "DEFINE TABLE relates_to" in schema_content
        assert "TYPE RELATION" in schema_content
        assert "IN memory OUT memory" in schema_content

    def test_relates_to_has_strength(self, schema_content: str) -> None:
        """relates_to should have a strength field clamped 0.0-1.0."""
        assert "DEFINE FIELD strength ON relates_to TYPE float" in schema_content

    def test_relates_to_has_reason(self, schema_content: str) -> None:
        """relates_to should have a reason field."""
        assert "DEFINE FIELD reason ON relates_to TYPE string" in schema_content

    def test_relates_to_has_auto_flag(self, schema_content: str) -> None:
        """relates_to should have an auto bool field."""
        assert "DEFINE FIELD auto ON relates_to TYPE bool DEFAULT false" in schema_content


class TestProjectTable:
    """Verify the project table definition."""

    def test_defines_project_table(self, schema_content: str) -> None:
        """Schema should define the project table as SCHEMAFULL."""
        assert "DEFINE TABLE project SCHEMAFULL" in schema_content

    def test_project_has_name(self, schema_content: str) -> None:
        """Project table should have a name field."""
        assert "DEFINE FIELD name ON project TYPE string" in schema_content

    def test_project_has_prefix(self, schema_content: str) -> None:
        """Project table should have a prefix field."""
        assert "DEFINE FIELD prefix ON project TYPE string" in schema_content

    def test_project_has_description(self, schema_content: str) -> None:
        """Project table should have an optional description field."""
        assert "DEFINE FIELD description ON project TYPE option<string>" in schema_content

    def test_project_prefix_unique_index(self, schema_content: str) -> None:
        """Project should have a unique index on prefix."""
        assert "project_prefix" in schema_content
        assert "UNIQUE" in schema_content


class TestTaskTable:
    """Verify the task table definition."""

    def test_defines_task_table(self, schema_content: str) -> None:
        """Schema should define the task table as SCHEMAFULL with CHANGEFEED."""
        assert "DEFINE TABLE task SCHEMAFULL CHANGEFEED 30d" in schema_content

    def test_task_has_task_id(self, schema_content: str) -> None:
        """Task table should have a task_id field."""
        assert "DEFINE FIELD task_id ON task TYPE string" in schema_content

    def test_task_has_project_ref(self, schema_content: str) -> None:
        """Task table should have a project record reference."""
        assert "DEFINE FIELD project ON task TYPE record<project>" in schema_content

    def test_task_has_name(self, schema_content: str) -> None:
        """Task table should have a name field."""
        assert "DEFINE FIELD name ON task TYPE string" in schema_content

    def test_task_has_type_assert(self, schema_content: str) -> None:
        """Task type should be constrained to task/epic."""
        assert 'DEFINE FIELD type ON task' in schema_content
        assert '$value IN ["task", "epic"]' in schema_content

    def test_task_has_status_assert(self, schema_content: str) -> None:
        """Task status should be constrained to valid values."""
        assert '"pending"' in schema_content
        assert '"in_progress"' in schema_content
        assert '"done"' in schema_content
        assert '"blocked"' in schema_content

    def test_task_has_priority_assert(self, schema_content: str) -> None:
        """Task priority should be constrained between 1 and 5."""
        assert "$value >= 1" in schema_content
        assert "$value <= 5" in schema_content

    def test_task_id_unique_index(self, schema_content: str) -> None:
        """Task should have a unique index on task_id."""
        assert "task_id_idx" in schema_content

    def test_task_status_index(self, schema_content: str) -> None:
        """Task should have an index on status."""
        assert "task_status" in schema_content

    def test_task_project_index(self, schema_content: str) -> None:
        """Task should have an index on project."""
        assert "task_project" in schema_content


class TestViews:
    """Verify the view definitions."""

    def test_recent_failures_view(self, schema_content: str) -> None:
        """Schema should define a recent_failures view."""
        assert "DEFINE TABLE recent_failures AS" in schema_content
        assert "outcome" in schema_content
        assert "failure" in schema_content

    def test_active_knowledge_view(self, schema_content: str) -> None:
        """Schema should define an active_knowledge view."""
        assert "DEFINE TABLE active_knowledge AS" in schema_content
        assert "confidence > 0.5" in schema_content

    def test_pending_tasks_view(self, schema_content: str) -> None:
        """Schema should define a pending_tasks view."""
        assert "DEFINE TABLE pending_tasks AS" in schema_content
        assert 'status = "pending"' in schema_content

    def test_no_auto_link_event(self, schema_content: str) -> None:
        """Schema should NOT define the auto_link event (handled in Python)."""
        assert "DEFINE EVENT auto_link" not in schema_content
