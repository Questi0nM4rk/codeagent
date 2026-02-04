-- CodeAgent Unified Database Schema
-- SurrealDB v2.x schema definition for memory, episodes, and codebase chunks

-- ============================================================================
-- Memory table (from A-MEM)
-- Stores semantic knowledge with automatic linking capabilities
-- ============================================================================

DEFINE TABLE memory SCHEMAFULL;

DEFINE FIELD content ON memory TYPE string
    ASSERT $value != NONE AND $value != "";

DEFINE FIELD keywords ON memory TYPE array<string>
    DEFAULT [];

DEFINE FIELD context ON memory TYPE string
    DEFAULT "";

DEFINE FIELD tags ON memory TYPE array<string>
    DEFAULT [];

DEFINE FIELD embedding ON memory TYPE array<float>
    ASSERT array::len($value) == 1536 OR array::len($value) == 0;

DEFINE FIELD created_at ON memory TYPE datetime
    DEFAULT time::now();

DEFINE FIELD updated_at ON memory TYPE datetime
    DEFAULT time::now();

-- Vector index for semantic similarity search (OpenAI embedding dimension)
DEFINE INDEX memory_embedding ON memory FIELDS embedding MTREE DIMENSION 1536;

-- Full-text search on content
DEFINE INDEX memory_content_search ON memory FIELDS content SEARCH ANALYZER ascii BM25;

-- Tag filtering
DEFINE INDEX memory_tags ON memory FIELDS tags;


-- ============================================================================
-- Episode table (from Reflection)
-- Stores episodic memory of task attempts for learning from experience
-- ============================================================================

DEFINE TABLE episode SCHEMAFULL;

DEFINE FIELD task ON episode TYPE string
    ASSERT $value != NONE AND $value != "";

DEFINE FIELD approach ON episode TYPE string
    DEFAULT "";

DEFINE FIELD outcome ON episode TYPE string
    ASSERT $value IN ["success", "partial", "failure"]
    DEFAULT "failure";

DEFINE FIELD feedback ON episode TYPE string
    DEFAULT "";

DEFINE FIELD feedback_type ON episode TYPE string
    DEFAULT "";

DEFINE FIELD reflection ON episode TYPE object
    DEFAULT {};

DEFINE FIELD code_context ON episode TYPE option<string>;

DEFINE FIELD file_path ON episode TYPE option<string>;

DEFINE FIELD tags ON episode TYPE array<string>
    DEFAULT [];

DEFINE FIELD model_used ON episode TYPE option<string>;

DEFINE FIELD backlog_task_id ON episode TYPE option<string>;

DEFINE FIELD effectiveness_score ON episode TYPE option<float>;

DEFINE FIELD created_at ON episode TYPE datetime
    DEFAULT time::now();

-- Index for finding similar tasks
DEFINE INDEX episode_task ON episode FIELDS task SEARCH ANALYZER ascii BM25;

-- Filter by outcome
DEFINE INDEX episode_outcome ON episode FIELDS outcome;

-- Filter by model
DEFINE INDEX episode_model ON episode FIELDS model_used;


-- ============================================================================
-- Chunk table (from codebase-mcp)
-- Stores code chunks for semantic code search
-- ============================================================================

DEFINE TABLE chunk SCHEMAFULL;

DEFINE FIELD file_path ON chunk TYPE string
    ASSERT $value != NONE AND $value != "";

DEFINE FIELD content ON chunk TYPE string
    ASSERT $value != NONE;

DEFINE FIELD language ON chunk TYPE string
    DEFAULT "unknown";

DEFINE FIELD symbol_type ON chunk TYPE option<string>;

DEFINE FIELD symbol_name ON chunk TYPE option<string>;

DEFINE FIELD start_line ON chunk TYPE int
    ASSERT $value >= 0
    DEFAULT 0;

DEFINE FIELD end_line ON chunk TYPE int
    ASSERT $value >= 0
    DEFAULT 0;

DEFINE FIELD embedding ON chunk TYPE array<float>
    ASSERT array::len($value) == 1536 OR array::len($value) == 0;

DEFINE FIELD project ON chunk TYPE string
    ASSERT $value != NONE AND $value != "";

DEFINE FIELD hash ON chunk TYPE string
    DEFAULT "";

DEFINE FIELD created_at ON chunk TYPE datetime
    DEFAULT time::now();

DEFINE FIELD updated_at ON chunk TYPE datetime
    DEFAULT time::now();

-- Vector index for semantic code search
DEFINE INDEX chunk_embedding ON chunk FIELDS embedding MTREE DIMENSION 1536;

-- Project filtering
DEFINE INDEX chunk_project ON chunk FIELDS project;

-- File path lookup
DEFINE INDEX chunk_file_path ON chunk FIELDS file_path;

-- Symbol lookup
DEFINE INDEX chunk_symbol ON chunk FIELDS symbol_name;

-- Deduplication by hash
DEFINE INDEX chunk_hash ON chunk FIELDS hash UNIQUE;


-- ============================================================================
-- Memory links (graph relationships)
-- Tracks automatic associations between memories (Zettelkasten-style)
-- ============================================================================

DEFINE TABLE links SCHEMAFULL TYPE RELATION FROM memory TO memory;

DEFINE FIELD strength ON links TYPE float
    ASSERT $value >= 0.0 AND $value <= 1.0
    DEFAULT 0.5;

DEFINE FIELD link_type ON links TYPE string
    DEFAULT "semantic";

DEFINE FIELD created_at ON links TYPE datetime
    DEFAULT time::now();

-- Index for traversing links by strength
DEFINE INDEX links_strength ON links FIELDS strength;


-- ============================================================================
-- Lesson links (episode effectiveness tracking)
-- Tracks which lessons helped in subsequent episodes
-- ============================================================================

DEFINE TABLE lesson_link SCHEMAFULL TYPE RELATION FROM episode TO episode;

DEFINE FIELD led_to_success ON lesson_link TYPE bool
    DEFAULT false;

DEFINE FIELD created_at ON lesson_link TYPE datetime
    DEFAULT time::now();


-- ============================================================================
-- Backlog tasks (single-task exposure)
-- Prevents scope creep by exposing only one task at a time
-- ============================================================================

DEFINE TABLE backlog SCHEMAFULL;

DEFINE FIELD title ON backlog TYPE string
    ASSERT $value != NONE AND $value != "";

DEFINE FIELD description ON backlog TYPE string
    DEFAULT "";

DEFINE FIELD status ON backlog TYPE string
    ASSERT $value IN ["pending", "in_progress", "blocked", "completed", "cancelled"]
    DEFAULT "pending";

DEFINE FIELD priority ON backlog TYPE int
    ASSERT $value >= 1 AND $value <= 5
    DEFAULT 3;

DEFINE FIELD suggested_model ON backlog TYPE string
    DEFAULT "haiku";

DEFINE FIELD parent_task_id ON backlog TYPE option<record<backlog>>;

DEFINE FIELD dependencies ON backlog TYPE array<record<backlog>>
    DEFAULT [];

DEFINE FIELD tags ON backlog TYPE array<string>
    DEFAULT [];

DEFINE FIELD created_at ON backlog TYPE datetime
    DEFAULT time::now();

DEFINE FIELD updated_at ON backlog TYPE datetime
    DEFAULT time::now();

-- Status filtering
DEFINE INDEX backlog_status ON backlog FIELDS status;

-- Priority sorting
DEFINE INDEX backlog_priority ON backlog FIELDS priority;
