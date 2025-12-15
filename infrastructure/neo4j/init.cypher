// ============================================
// CodeAgent Neo4j Schema Initialization
// Run once on first startup to create indexes and constraints
// Version: 2.0.0
// ============================================

// ============================================
// CONSTRAINTS (unique identifiers)
// ============================================

// Primary node constraint - matches code-graph-mcp
CREATE CONSTRAINT code_node_id IF NOT EXISTS
FOR (n:CodeNode) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT file_path IF NOT EXISTS
FOR (f:File) REQUIRE f.path IS UNIQUE;

CREATE CONSTRAINT import_name IF NOT EXISTS
FOR (i:Import) REQUIRE i.name IS UNIQUE;

// ============================================
// BASIC INDEXES (query performance)
// ============================================

// Name-based lookups (most common query pattern)
CREATE INDEX code_node_name IF NOT EXISTS
FOR (n:CodeNode) ON (n.name);

CREATE INDEX code_node_full_name IF NOT EXISTS
FOR (n:CodeNode) ON (n.full_name);

// Type filtering (function, class, struct, etc.)
CREATE INDEX code_node_type IF NOT EXISTS
FOR (n:CodeNode) ON (n.type);

// File-based lookups
CREATE INDEX code_node_file IF NOT EXISTS
FOR (n:CodeNode) ON (n.file);

// Line number lookups
CREATE INDEX code_node_line IF NOT EXISTS
FOR (n:CodeNode) ON (n.line);

// ============================================
// COMPOSITE INDEXES (common query patterns)
// ============================================

// Find all entities of a type in a file (very common)
CREATE INDEX code_node_file_type IF NOT EXISTS
FOR (n:CodeNode) ON (n.file, n.type);

// Find entities by name and type
CREATE INDEX code_node_name_type IF NOT EXISTS
FOR (n:CodeNode) ON (n.name, n.type);

// File language filtering
CREATE INDEX file_language IF NOT EXISTS
FOR (f:File) ON (f.language);

// ============================================
// FULL-TEXT SEARCH INDEXES (semantic search)
// ============================================

// Full-text index on code names for fuzzy searching
// Supports: contains, starts with, ends with, fuzzy match
CREATE FULLTEXT INDEX code_name_search IF NOT EXISTS
FOR (n:CodeNode)
ON EACH [n.name, n.full_name];

// Full-text index on file paths
CREATE FULLTEXT INDEX file_path_search IF NOT EXISTS
FOR (f:File)
ON EACH [f.path];

// Full-text index on import names
CREATE FULLTEXT INDEX import_name_search IF NOT EXISTS
FOR (i:Import)
ON EACH [i.name];

// ============================================
// NODE LABELS
// ============================================
// :CodeNode    - Any code entity (class, function, struct, etc.)
//   Properties:
//   - id: Unique identifier (file:line:name)
//   - type: Entity type (class, function, struct, interface, trait, etc.)
//   - name: Short name
//   - full_name: Fully qualified name (including parent scope)
//   - file: File path
//   - line: Start line number
//   - end_line: End line number
//
// :File        - Source file
//   Properties:
//   - path: Absolute file path
//   - last_indexed: Timestamp of last indexing
//   - language: Programming language
//
// :Import      - Import/using statement
//   Properties:
//   - name: Imported module/namespace name

// ============================================
// RELATIONSHIP TYPES
// ============================================
// (:CodeNode)-[:CALLS]->(:CodeNode)
//   Function/method calls another function/method
//   Properties:
//   - file: File where call occurs
//   - line: Line number of call
//
// (:CodeNode)-[:CONTAINS]->(:CodeNode)
//   Parent contains child (class contains method)
//
// (:CodeNode)-[:INHERITS]->(:CodeNode)
//   Class inherits from another class
//
// (:CodeNode)-[:IMPLEMENTS]->(:CodeNode)
//   Class implements interface/trait
//
// (:CodeNode)-[:USES]->(:CodeNode)
//   Code uses another entity (field access, type reference)
//
// (:File)-[:IMPORTS]->(:Import)
//   File imports a module/namespace
//
// (:File)-[:DEFINES]->(:CodeNode)
//   File defines a code entity

// ============================================
// SAMPLE QUERIES (for reference)
// ============================================

// Find all functions in a file:
// MATCH (n:CodeNode {type: 'function'})
// WHERE n.file ENDS WITH 'MyFile.cs'
// RETURN n ORDER BY n.line

// Find what calls a function:
// MATCH (caller:CodeNode)-[:CALLS]->(callee:CodeNode {name: 'MyFunction'})
// RETURN caller.file, caller.name, caller.line

// Find impact of changing a function:
// MATCH (affected:CodeNode)-[:CALLS*1..5]->(changed:CodeNode {name: 'MyFunction'})
// RETURN DISTINCT affected.file, affected.name, affected.line

// Get call graph from entry point:
// MATCH path = (start:CodeNode {name: 'Main'})-[:CALLS*1..3]->(called)
// RETURN path

// Search for symbols by name pattern:
// MATCH (n:CodeNode)
// WHERE toLower(n.name) CONTAINS 'user'
// RETURN n.name, n.file, n.line, n.type
// LIMIT 20

// Find circular dependencies:
// MATCH path = (a:CodeNode)-[:CALLS*]->(a)
// RETURN path
