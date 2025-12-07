// CodeAgent Neo4j Schema Initialization
// Run once on first startup to create indexes and constraints

// ============================================
// CONSTRAINTS (unique identifiers)
// ============================================

CREATE CONSTRAINT file_path IF NOT EXISTS
FOR (f:File) REQUIRE f.path IS UNIQUE;

CREATE CONSTRAINT function_id IF NOT EXISTS
FOR (fn:Function) REQUIRE fn.id IS UNIQUE;

CREATE CONSTRAINT class_id IF NOT EXISTS
FOR (c:Class) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT namespace_id IF NOT EXISTS
FOR (n:Namespace) REQUIRE n.id IS UNIQUE;

// ============================================
// INDEXES (query performance)
// ============================================

CREATE INDEX file_language IF NOT EXISTS
FOR (f:File) ON (f.language);

CREATE INDEX function_name IF NOT EXISTS
FOR (fn:Function) ON (fn.name);

CREATE INDEX class_name IF NOT EXISTS
FOR (c:Class) ON (c.name);

CREATE INDEX node_type IF NOT EXISTS
FOR (n:CodeNode) ON (n.type);

// Full-text search for code content
CREATE FULLTEXT INDEX code_search IF NOT EXISTS
FOR (n:Function|Class|File) ON EACH [n.name, n.content];

// ============================================
// NODE LABELS
// ============================================
// :File        - Source files
// :Function    - Functions/methods
// :Class       - Classes/structs/interfaces
// :Namespace   - Namespaces/modules
// :Parameter   - Function parameters
// :Import      - Import statements
// :CodeNode    - Generic code element

// ============================================
// RELATIONSHIP TYPES
// ============================================
// :CONTAINS    - File contains class/function
// :CALLS       - Function calls function
// :IMPORTS     - File imports file/module
// :INHERITS    - Class inherits from class
// :IMPLEMENTS  - Class implements interface
// :DEPENDS_ON  - Generic dependency
// :RETURNS     - Function returns type
// :PARAMETER   - Function has parameter

// ============================================
// SAMPLE QUERIES (for reference)
// ============================================

// Find all callers of a function:
// MATCH (caller:Function)-[:CALLS]->(target:Function {name: $name})
// RETURN caller

// Find impact of changing a file:
// MATCH (f:File {path: $path})-[:CONTAINS]->(fn:Function)
// MATCH (caller:Function)-[:CALLS]->(fn)
// RETURN DISTINCT caller.file AS affected_file, caller.name AS affected_function

// Find dependency chain:
// MATCH path = (start:File {path: $path})-[:IMPORTS*1..5]->(dep:File)
// RETURN path

// Search for code by name:
// CALL db.index.fulltext.queryNodes('code_search', $query)
// YIELD node, score
// RETURN node, score ORDER BY score DESC LIMIT 10
