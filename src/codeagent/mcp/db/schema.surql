-- CodeAgent Unified Database Schema
-- SurrealDB v2.x schema for the unified MCP server
-- Reference: docs/surrealdb-schema-reference.md

-- ============================================================================
-- Analyzer
-- Custom text analyzer for full-text search across memory content
-- ============================================================================

DEFINE ANALYZER memory_analyzer
    TOKENIZERS blank, class, camel, punct
    FILTERS snowball(english), lowercase;

-- ============================================================================
-- Memory Table
-- Core table. All memory types live here with a type discriminator.
-- Stores semantic knowledge, episodes, decisions, patterns, and code chunks.
-- ============================================================================

DEFINE TABLE memory SCHEMAFULL CHANGEFEED 90d;

-- Core fields
DEFINE FIELD type ON memory TYPE string
    ASSERT $value IN ["knowledge", "episode", "decision", "pattern", "code_chunk"];
DEFINE FIELD content ON memory TYPE string;
DEFINE FIELD title ON memory TYPE option<string>;
DEFINE FIELD metadata ON memory FLEXIBLE TYPE object;
DEFINE FIELD embedding ON memory TYPE array<float>;
DEFINE FIELD tags ON memory TYPE array<string> DEFAULT [];
DEFINE FIELD project ON memory TYPE option<string>;
DEFINE FIELD confidence ON memory TYPE float DEFAULT 1.0;
DEFINE FIELD access_count ON memory TYPE int DEFAULT 0;
DEFINE FIELD last_accessed ON memory TYPE option<datetime>;
DEFINE FIELD source_task ON memory TYPE option<record<task>>;
DEFINE FIELD created_at ON memory TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON memory TYPE datetime DEFAULT time::now();

-- Indexes
DEFINE INDEX memory_vec ON memory FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE TYPE F32 EFC 200 M 16;
DEFINE INDEX memory_fts ON memory FIELDS content
    SEARCH ANALYZER memory_analyzer BM25 HIGHLIGHTS;
DEFINE INDEX memory_type ON memory FIELDS type;
DEFINE INDEX memory_project ON memory FIELDS project;
DEFINE INDEX memory_tags ON memory FIELDS tags;

-- ============================================================================
-- Graph Relations (relates_to)
-- Zettelkasten-style bidirectional links between memories.
-- Auto-linking is handled in Python, not as a DB event.
-- ============================================================================

DEFINE TABLE relates_to SCHEMAFULL TYPE RELATION IN memory OUT memory;

DEFINE FIELD strength ON relates_to TYPE float
    ASSERT $value >= 0.0 AND $value <= 1.0;
DEFINE FIELD reason ON relates_to TYPE string;
DEFINE FIELD auto ON relates_to TYPE bool DEFAULT false;
DEFINE FIELD created_at ON relates_to TYPE datetime DEFAULT time::now();

-- ============================================================================
-- Project Table
-- Tracks project metadata for task organization.
-- ============================================================================

DEFINE TABLE project SCHEMAFULL;

DEFINE FIELD name ON project TYPE string;
DEFINE FIELD prefix ON project TYPE string;
DEFINE FIELD description ON project TYPE option<string>;
DEFINE FIELD created_at ON project TYPE datetime DEFAULT time::now();

DEFINE INDEX project_prefix ON project FIELDS prefix UNIQUE;

-- ============================================================================
-- Task Table
-- Tracks work items with priority, status, and file boundaries.
-- ============================================================================

DEFINE TABLE task SCHEMAFULL CHANGEFEED 30d;

DEFINE FIELD task_id ON task TYPE string;
DEFINE FIELD project ON task TYPE record<project>;
DEFINE FIELD name ON task TYPE string;
DEFINE FIELD type ON task TYPE string DEFAULT "task"
    ASSERT $value IN ["task", "epic"];
DEFINE FIELD description ON task TYPE option<string>;
DEFINE FIELD status ON task TYPE string DEFAULT "pending"
    ASSERT $value IN ["pending", "in_progress", "done", "blocked"];
DEFINE FIELD priority ON task TYPE int DEFAULT 3
    ASSERT $value >= 1 AND $value <= 5;
DEFINE FIELD files_exclusive ON task TYPE array<string> DEFAULT [];
DEFINE FIELD files_readonly ON task TYPE array<string> DEFAULT [];
DEFINE FIELD depends_on ON task TYPE array<record<task>> DEFAULT [];
DEFINE FIELD parent ON task TYPE option<record<task>>;
DEFINE FIELD resolved_by ON task TYPE option<record<memory>>;
DEFINE FIELD suggested_model ON task TYPE option<string>;
DEFINE FIELD created_at ON task TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON task TYPE datetime DEFAULT time::now();

DEFINE INDEX task_id_idx ON task FIELDS task_id UNIQUE;
DEFINE INDEX task_status ON task FIELDS status;
DEFINE INDEX task_project ON task FIELDS project;

-- ============================================================================
-- Views
-- Pre-computed virtual tables for hot query paths.
-- ============================================================================

DEFINE TABLE recent_failures AS
    SELECT * FROM memory
    WHERE type = "episode" AND metadata.outcome = "failure"
    ORDER BY created_at DESC LIMIT 50;

DEFINE TABLE active_knowledge AS
    SELECT * FROM memory
    WHERE type = "knowledge" AND confidence > 0.5
    ORDER BY access_count DESC LIMIT 100;

DEFINE TABLE pending_tasks AS
    SELECT * FROM task
    WHERE status = "pending"
    ORDER BY priority ASC, created_at ASC;
