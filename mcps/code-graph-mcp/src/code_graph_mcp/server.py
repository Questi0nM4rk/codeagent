"""
Code Graph MCP Server

AST-based code knowledge graph using Neo4j and Tree-sitter.
Based on research showing 75% improvement on code retrieval tasks.

Tools:
- index_file: Parse file and add to knowledge graph
- index_directory: Recursively index a directory
- query_dependencies: Find code dependencies for a symbol
- find_affected_by_change: Find code affected by changes to a function
- find_similar_code: Find code similar to a description
- get_call_graph: Get call graph from an entry point
- search_symbols: Search for symbols by name pattern
- get_file_structure: Get structure of a file
- get_graph_stats: Get statistics about the graph

Supported Languages:
- C# (.cs)
- C/C++ (.cpp, .cc, .cxx, .c, .h, .hpp)
- Rust (.rs)
- Lua (.lua)
- Bash (.sh, .bash, .zsh)
- Python (.py)
- TypeScript/JavaScript (.ts, .tsx, .js, .jsx)
- Go (.go)

Relationships:
- CALLS: Function calls another function
- CONTAINS: Parent contains child (class→method)
- INHERITS: Class inherits from another
- IMPLEMENTS: Class implements interface/trait
- USES: Code uses a type (field, parameter, return type)
- IMPORTS: File imports module
- DEFINES: File defines code entity
"""

import os
import logging
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeNode:
    """Represents a code entity."""
    id: str
    type: str
    name: str
    full_name: str
    file: str
    line: int
    end_line: int = 0


@dataclass
class Relationship:
    """Represents a relationship between code entities."""
    from_id: str
    to_name: str  # May be just a name if target not yet indexed
    rel_type: str  # CALLS, CONTAINS, INHERITS, IMPLEMENTS, USES
    file: str
    line: int


@dataclass
class ExtractionResult:
    """Result of AST extraction."""
    nodes: list[CodeNode] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)

# Initialize FastMCP server
mcp = FastMCP(
    "code-graph",
    instructions="Code knowledge graph for AST-based code analysis. "
    "Use this to understand code structure, dependencies, and relationships.",
)

# Neo4j connection settings
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "codeagent")

# Global driver instance
_driver = None


def get_driver():
    """Get or create Neo4j driver."""
    global _driver
    if _driver is None:
        try:
            _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
            _driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {NEO4J_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    return _driver


def close_driver():
    """Close Neo4j driver."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None


# Language-specific tree-sitter parsers
_parsers = {}


def get_parser(extension: str):
    """Get tree-sitter parser for file extension."""
    if extension in _parsers:
        return _parsers[extension]

    try:
        import tree_sitter

        parser = tree_sitter.Parser()
        lang = None

        if extension in (".cs",):
            import tree_sitter_c_sharp as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".cpp", ".cc", ".cxx", ".c", ".h", ".hpp"):
            import tree_sitter_cpp as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".rs",):
            import tree_sitter_rust as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".lua",):
            import tree_sitter_lua as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".sh", ".bash", ".zsh"):
            import tree_sitter_bash as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".py",):
            import tree_sitter_python as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".ts", ".tsx"):
            import tree_sitter_typescript as ts_lang
            lang = tree_sitter.Language(ts_lang.language_typescript())
        elif extension in (".js", ".jsx"):
            import tree_sitter_javascript as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        elif extension in (".go",):
            import tree_sitter_go as ts_lang
            lang = tree_sitter.Language(ts_lang.language())
        else:
            return None

        parser.language = lang
        _parsers[extension] = parser
        return parser
    except ImportError as e:
        logger.warning(f"Tree-sitter language not available for {extension}: {e}")
        return None


def get_language_name(extension: str) -> str:
    """Get language name from extension."""
    lang_map = {
        ".cs": "csharp",
        ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".c": "c", ".h": "c", ".hpp": "cpp",
        ".rs": "rust",
        ".lua": "lua",
        ".sh": "bash", ".bash": "bash", ".zsh": "bash",
        ".py": "python",
        ".ts": "typescript", ".tsx": "typescript",
        ".js": "javascript", ".jsx": "javascript",
        ".go": "go",
    }
    return lang_map.get(extension, "unknown")


def extract_code(node, file_path: str, result: ExtractionResult | None = None,
                  parent_id: str = "", parent_name: str = "", language: str = "") -> ExtractionResult:
    """
    Extract code nodes and relationships from AST.

    Extracts:
    - Nodes: classes, functions, structs, interfaces, traits, modules
    - Relationships: CALLS, CONTAINS, INHERITS, IMPLEMENTS, USES
    """
    if result is None:
        result = ExtractionResult()

    # Map tree-sitter node types to our types (expanded for all languages)
    type_map = {
        # C#
        "class_declaration": "class",
        "interface_declaration": "interface",
        "struct_declaration": "struct",
        "record_declaration": "class",
        "enum_declaration": "enum",
        "method_declaration": "function",
        "constructor_declaration": "constructor",
        "property_declaration": "property",
        "field_declaration": "field",
        "namespace_declaration": "namespace",
        "using_directive": "import",
        # C/C++
        "function_definition": "function",
        "class_specifier": "class",
        "struct_specifier": "struct",
        "enum_specifier": "enum",
        "preproc_include": "import",
        "declaration": "field",
        # Rust
        "function_item": "function",
        "impl_item": "impl",
        "struct_item": "struct",
        "enum_item": "enum",
        "trait_item": "trait",
        "mod_item": "module",
        "use_declaration": "import",
        "const_item": "const",
        "static_item": "static",
        # Lua
        "function_declaration": "function",
        "local_function": "function",
        # Bash
        "function_definition": "function",
        # Python
        "class_definition": "class",
        "function_definition": "function",
        "import_statement": "import",
        "import_from_statement": "import",
        # TypeScript/JavaScript
        "class_declaration": "class",
        "function_declaration": "function",
        "method_definition": "function",
        "arrow_function": "function",
        "interface_declaration": "interface",
        "type_alias_declaration": "type",
        "enum_declaration": "enum",
        "import_statement": "import",
        # Go
        "function_declaration": "function",
        "method_declaration": "function",
        "type_declaration": "type",
        "type_spec": "struct",
        "import_declaration": "import",
    }

    # Container types that can have children
    container_types = {"class", "struct", "namespace", "module", "impl", "interface", "trait"}

    current_id = parent_id
    current_name = parent_name

    # Handle entity declarations
    if node.type in type_map:
        entity_type = type_map[node.type]

        # Get name
        name_node = node.child_by_field_name("name")
        if name_node:
            name = name_node.text.decode()
        else:
            # Try alternative name extraction
            for child in node.children:
                if child.type in ("identifier", "type_identifier", "name"):
                    name = child.text.decode()
                    break
            else:
                name = f"anonymous_{node.start_point[0]}"

        full_name = f"{parent_name}.{name}" if parent_name else name
        node_id = f"{file_path}:{node.start_point[0]}:{name}"

        # Skip imports, handle them separately
        if entity_type != "import":
            code_node = CodeNode(
                id=node_id,
                type=entity_type,
                name=name,
                full_name=full_name,
                file=file_path,
                line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
            )
            result.nodes.append(code_node)

            # CONTAINS relationship (parent contains this node)
            if parent_id:
                result.relationships.append(Relationship(
                    from_id=parent_id,
                    to_name=name,
                    rel_type="CONTAINS",
                    file=file_path,
                    line=node.start_point[0] + 1,
                ))

            # Update context for children
            if entity_type in container_types:
                current_id = node_id
                current_name = full_name

            # Extract inheritance (base classes)
            _extract_inheritance(node, node_id, file_path, result, language)

    # Handle imports
    if node.type in ("using_directive", "import_statement", "import_from_statement",
                     "use_declaration", "preproc_include", "import_declaration"):
        import_name = _extract_import_name(node)
        if import_name:
            result.imports.append(import_name)

    # Handle function calls (CALLS relationship)
    if node.type in ("call_expression", "invocation_expression", "function_call", "method_invocation"):
        callee_name = _extract_call_name(node)
        if callee_name and current_id:
            result.relationships.append(Relationship(
                from_id=current_id,
                to_name=callee_name,
                rel_type="CALLS",
                file=file_path,
                line=node.start_point[0] + 1,
            ))

    # Handle type references (USES relationship)
    if node.type in ("type_identifier", "generic_type", "type_annotation", "type"):
        type_name = node.text.decode() if node.text else None
        if type_name and current_id and len(type_name) < 100:  # Skip very long types
            # Clean up generic types
            if "<" in type_name:
                type_name = type_name.split("<")[0]
            if type_name not in ("void", "int", "string", "bool", "float", "double", "char", "byte"):
                result.relationships.append(Relationship(
                    from_id=current_id,
                    to_name=type_name,
                    rel_type="USES",
                    file=file_path,
                    line=node.start_point[0] + 1,
                ))

    # Recurse into children
    for child in node.children:
        extract_code(child, file_path, result, current_id, current_name, language)

    return result


def _extract_inheritance(node, node_id: str, file_path: str, result: ExtractionResult, language: str):
    """Extract inheritance and implementation relationships."""

    # C# base_list: class Foo : Bar, IInterface
    if language == "csharp":
        for child in node.children:
            if child.type == "base_list":
                for base in child.children:
                    if base.type in ("identifier", "generic_name", "qualified_name"):
                        base_name = base.text.decode()
                        # Heuristic: interfaces start with I
                        rel_type = "IMPLEMENTS" if base_name.startswith("I") else "INHERITS"
                        result.relationships.append(Relationship(
                            from_id=node_id,
                            to_name=base_name,
                            rel_type=rel_type,
                            file=file_path,
                            line=base.start_point[0] + 1,
                        ))

    # C++ base_class_clause: class Foo : public Bar
    elif language in ("cpp", "c"):
        for child in node.children:
            if child.type == "base_class_clause":
                for specifier in child.children:
                    if specifier.type == "type_identifier":
                        result.relationships.append(Relationship(
                            from_id=node_id,
                            to_name=specifier.text.decode(),
                            rel_type="INHERITS",
                            file=file_path,
                            line=specifier.start_point[0] + 1,
                        ))

    # Rust impl blocks: impl Trait for Struct
    elif language == "rust":
        if node.type == "impl_item":
            trait_node = node.child_by_field_name("trait")
            type_node = node.child_by_field_name("type")
            if trait_node and type_node:
                result.relationships.append(Relationship(
                    from_id=f"{file_path}:{node.start_point[0]}:{type_node.text.decode()}",
                    to_name=trait_node.text.decode(),
                    rel_type="IMPLEMENTS",
                    file=file_path,
                    line=node.start_point[0] + 1,
                ))

    # Python class inheritance: class Foo(Bar, Baz)
    elif language == "python":
        for child in node.children:
            if child.type == "argument_list":
                for arg in child.children:
                    if arg.type == "identifier":
                        result.relationships.append(Relationship(
                            from_id=node_id,
                            to_name=arg.text.decode(),
                            rel_type="INHERITS",
                            file=file_path,
                            line=arg.start_point[0] + 1,
                        ))

    # TypeScript/JavaScript extends/implements
    elif language in ("typescript", "javascript"):
        for child in node.children:
            if child.type == "extends_clause":
                for type_node in child.children:
                    if type_node.type in ("identifier", "type_identifier"):
                        result.relationships.append(Relationship(
                            from_id=node_id,
                            to_name=type_node.text.decode(),
                            rel_type="INHERITS",
                            file=file_path,
                            line=type_node.start_point[0] + 1,
                        ))
            elif child.type == "implements_clause":
                for type_node in child.children:
                    if type_node.type in ("identifier", "type_identifier"):
                        result.relationships.append(Relationship(
                            from_id=node_id,
                            to_name=type_node.text.decode(),
                            rel_type="IMPLEMENTS",
                            file=file_path,
                            line=type_node.start_point[0] + 1,
                        ))


def _extract_import_name(node) -> str | None:
    """Extract import name from various import statement types."""
    if node.type == "using_directive":  # C#
        for child in node.children:
            if child.type in ("identifier", "qualified_name"):
                return child.text.decode()
    elif node.type in ("import_statement", "import_from_statement"):  # Python/JS
        for child in node.children:
            if child.type in ("dotted_name", "identifier", "string"):
                return child.text.decode().strip("'\"")
    elif node.type == "use_declaration":  # Rust
        for child in node.children:
            if child.type == "use_tree":
                return child.text.decode()
    elif node.type == "preproc_include":  # C/C++
        for child in node.children:
            if child.type in ("string_literal", "system_lib_string"):
                return child.text.decode().strip("<>\"")
    return None


def _extract_call_name(node) -> str | None:
    """Extract function name from call expression."""
    # Try function field first
    func = node.child_by_field_name("function")
    if func:
        if func.type == "identifier":
            return func.text.decode()
        elif func.type in ("member_expression", "field_expression", "scoped_identifier"):
            # Get the last part (method name)
            for child in reversed(func.children):
                if child.type in ("identifier", "field_identifier", "property_identifier"):
                    return child.text.decode()

    # Try name field
    name = node.child_by_field_name("name")
    if name:
        return name.text.decode()

    # Fallback: first identifier child
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode()

    return None


# Keep old function for backward compatibility but mark as deprecated
def extract_nodes(node, file_path: str, nodes: list | None = None, parent_name: str = ""):
    """Extract code nodes from AST. DEPRECATED: Use extract_code() instead."""
    if nodes is None:
        nodes = []

    # Use new extraction and convert to old format
    result = extract_code(node, file_path, language=get_language_name(Path(file_path).suffix))

    for code_node in result.nodes:
        nodes.append({
            "id": code_node.id,
            "type": code_node.type,
            "name": code_node.name,
            "full_name": code_node.full_name,
            "file": code_node.file,
            "line": code_node.line,
            "end_line": code_node.end_line,
        })

    # Add calls in old format
    for rel in result.relationships:
        if rel.rel_type == "CALLS":
            nodes.append({
                "id": f"{file_path}:{rel.line}:call",
                "type": "call",
                "name": rel.to_name,
                "file": rel.file,
                "line": rel.line,
                "caller": rel.from_id.split(":")[-1] if rel.from_id else "unknown",
            })

    return nodes


def store_extraction_result(result: ExtractionResult, file_path: str, language: str):
    """
    Store extraction result in Neo4j using batch operations.

    Uses UNWIND for efficient bulk inserts instead of individual statements.
    """
    driver = get_driver()

    with driver.session() as session:
        # First, remove old data from this file
        session.run(
            """
            MATCH (n:CodeNode {file: $file})
            DETACH DELETE n
            """,
            file=file_path,
        )

        # Also clean up file node
        session.run(
            """
            MATCH (f:File {path: $file})
            DETACH DELETE f
            """,
            file=file_path,
        )

        # Create/update file node
        session.run(
            """
            MERGE (f:File {path: $file})
            SET f.language = $language,
                f.last_indexed = datetime()
            """,
            file=file_path,
            language=language,
        )

        # Batch insert nodes using UNWIND
        if result.nodes:
            node_data = [
                {
                    "id": n.id,
                    "type": n.type,
                    "name": n.name,
                    "full_name": n.full_name,
                    "file": n.file,
                    "line": n.line,
                    "end_line": n.end_line,
                }
                for n in result.nodes
            ]
            session.run(
                """
                UNWIND $nodes AS node
                MERGE (n:CodeNode {id: node.id})
                SET n.type = node.type,
                    n.name = node.name,
                    n.full_name = node.full_name,
                    n.file = node.file,
                    n.line = node.line,
                    n.end_line = node.end_line
                WITH n, node
                MATCH (f:File {path: node.file})
                MERGE (f)-[:DEFINES]->(n)
                """,
                nodes=node_data,
            )

        # Batch insert relationships by type
        for rel_type in ["CALLS", "CONTAINS", "INHERITS", "IMPLEMENTS", "USES"]:
            rels = [r for r in result.relationships if r.rel_type == rel_type]
            if rels:
                rel_data = [
                    {
                        "from_id": r.from_id,
                        "to_name": r.to_name,
                        "file": r.file,
                        "line": r.line,
                    }
                    for r in rels
                ]
                session.run(
                    f"""
                    UNWIND $rels AS rel
                    MATCH (from:CodeNode {{id: rel.from_id}})
                    MERGE (to:CodeNode {{name: rel.to_name}})
                    MERGE (from)-[r:{rel_type} {{file: rel.file, line: rel.line}}]->(to)
                    """,
                    rels=rel_data,
                )

        # Insert imports
        if result.imports:
            import_data = [{"name": imp, "file": file_path} for imp in result.imports]
            session.run(
                """
                UNWIND $imports AS imp
                MATCH (f:File {path: imp.file})
                MERGE (i:Import {name: imp.name})
                MERGE (f)-[:IMPORTS]->(i)
                """,
                imports=import_data,
            )

    return {
        "nodes": len(result.nodes),
        "relationships": len(result.relationships),
        "imports": len(result.imports),
    }


def store_nodes_in_neo4j(nodes: list[dict], file_path: str):
    """Store extracted nodes in Neo4j. DEPRECATED: Use store_extraction_result() instead."""
    driver = get_driver()

    with driver.session() as session:
        # First, remove old nodes from this file
        session.run(
            """
            MATCH (n:CodeNode {file: $file})
            DETACH DELETE n
            """,
            file=file_path,
        )

        # Insert new nodes
        for node in nodes:
            if node["type"] == "call":
                # Store call relationships separately
                session.run(
                    """
                    MERGE (caller:CodeNode {full_name: $caller})
                    MERGE (callee:CodeNode {name: $callee_name})
                    MERGE (caller)-[:CALLS {file: $file, line: $line}]->(callee)
                    """,
                    caller=node.get("caller", "unknown"),
                    callee_name=node["name"],
                    file=node["file"],
                    line=node["line"],
                )
            elif node["type"] == "import":
                # Store import relationships
                session.run(
                    """
                    MERGE (file:File {path: $file})
                    MERGE (import:Import {name: $name})
                    MERGE (file)-[:IMPORTS]->(import)
                    """,
                    file=file_path,
                    name=node["name"],
                )
            else:
                # Store regular code nodes
                session.run(
                    """
                    MERGE (n:CodeNode {id: $id})
                    SET n.type = $type,
                        n.name = $name,
                        n.full_name = $full_name,
                        n.file = $file,
                        n.line = $line,
                        n.end_line = $end_line
                    """,
                    **node,
                )

    return len(nodes)


@mcp.tool()
def index_file(file_path: str) -> dict[str, Any]:
    """
    Parse a file and add its AST to the knowledge graph.

    Args:
        file_path: Absolute path to the file to index

    Returns:
        Dictionary with indexing results including node count
    """
    path = Path(file_path)

    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    if not path.is_file():
        return {"error": f"Not a file: {file_path}"}

    extension = path.suffix.lower()
    parser = get_parser(extension)

    supported_extensions = [
        ".cs", ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
        ".rs", ".lua", ".sh", ".bash", ".zsh",
        ".py", ".ts", ".tsx", ".js", ".jsx", ".go"
    ]

    if parser is None:
        return {"error": f"Unsupported file type: {extension}", "supported": supported_extensions}

    language = get_language_name(extension)

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = parser.parse(bytes(content, "utf8"))

        # Use new extraction function
        result = extract_code(tree.root_node, str(path), language=language)
        stats = store_extraction_result(result, str(path), language)

        # Collect unique types
        types = list(set(n.type for n in result.nodes))

        # Collect relationship stats
        rel_counts = {}
        for rel in result.relationships:
            rel_counts[rel.rel_type] = rel_counts.get(rel.rel_type, 0) + 1

        return {
            "indexed": True,
            "file": str(path),
            "language": language,
            "nodes": stats["nodes"],
            "relationships": stats["relationships"],
            "imports": stats["imports"],
            "types": types,
            "relationship_counts": rel_counts,
        }
    except Exception as e:
        logger.error(f"Error indexing {file_path}: {e}")
        return {"error": str(e), "file": file_path}


@mcp.tool()
def index_directory(directory: str, extensions: list[str] | None = None) -> dict[str, Any]:
    """
    Recursively index all supported files in a directory.

    Args:
        directory: Path to directory to index
        extensions: Optional list of extensions to include (e.g., [".cs", ".rs"])

    Returns:
        Summary of indexing results
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return {"error": f"Directory not found: {directory}"}

    if not dir_path.is_dir():
        return {"error": f"Not a directory: {directory}"}

    # All supported extensions including new languages
    supported = extensions or [
        ".cs",  # C#
        ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",  # C/C++
        ".rs",  # Rust
        ".lua",  # Lua
        ".sh", ".bash", ".zsh",  # Bash
        ".py",  # Python
        ".ts", ".tsx",  # TypeScript
        ".js", ".jsx",  # JavaScript
        ".go",  # Go
    ]
    results = {
        "indexed": 0,
        "failed": 0,
        "skipped": 0,
        "total_nodes": 0,
        "total_relationships": 0,
        "by_language": {},
        "files": [],
    }

    # Directories to skip
    skip_dirs = {
        "bin", "obj", "target", "node_modules", ".git", "__pycache__",
        "build", "dist", "vendor", ".venv", "venv", "env",
        ".idea", ".vscode", "coverage", ".next", ".nuxt",
    }

    for path in dir_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in supported:
            # Skip excluded directories
            if any(skip in path.parts for skip in skip_dirs):
                results["skipped"] += 1
                continue

            result = index_file(str(path))
            if "error" in result:
                results["failed"] += 1
            else:
                results["indexed"] += 1
                nodes = result.get("nodes", 0)
                rels = result.get("relationships", 0)
                lang = result.get("language", "unknown")

                results["total_nodes"] += nodes
                results["total_relationships"] += rels

                # Track by language
                if lang not in results["by_language"]:
                    results["by_language"][lang] = {"files": 0, "nodes": 0, "relationships": 0}
                results["by_language"][lang]["files"] += 1
                results["by_language"][lang]["nodes"] += nodes
                results["by_language"][lang]["relationships"] += rels

                results["files"].append({
                    "file": str(path),
                    "language": lang,
                    "nodes": nodes,
                    "relationships": rels,
                })

    return results


@mcp.tool()
def query_dependencies(symbol: str, depth: int = 3) -> dict[str, Any]:
    """
    Find all code that depends on or is depended by a symbol.

    Args:
        symbol: Name of the symbol to query (function, class, etc.)
        depth: How many levels of dependencies to traverse (1-5)

    Returns:
        Dictionary with incoming and outgoing dependencies
    """
    depth = min(max(depth, 1), 5)  # Clamp to 1-5
    driver = get_driver()

    with driver.session() as session:
        # Find what this symbol calls (outgoing)
        outgoing = session.run(
            """
            MATCH (n:CodeNode)
            WHERE n.name = $symbol OR n.full_name = $symbol
            MATCH (n)-[:CALLS*1..$depth]->(called:CodeNode)
            RETURN DISTINCT called.name AS name, called.file AS file, called.line AS line
            ORDER BY called.file, called.line
            """,
            symbol=symbol,
            depth=depth,
        )

        # Find what calls this symbol (incoming)
        incoming = session.run(
            """
            MATCH (n:CodeNode)
            WHERE n.name = $symbol OR n.full_name = $symbol
            MATCH (caller:CodeNode)-[:CALLS*1..$depth]->(n)
            RETURN DISTINCT caller.name AS name, caller.file AS file, caller.line AS line
            ORDER BY caller.file, caller.line
            """,
            symbol=symbol,
            depth=depth,
        )

        return {
            "symbol": symbol,
            "depth": depth,
            "calls": [dict(record) for record in outgoing],
            "called_by": [dict(record) for record in incoming],
        }


@mcp.tool()
def find_affected_by_change(file_path: str, function_name: str) -> dict[str, Any]:
    """
    Find all code affected if a function is modified.

    Args:
        file_path: Path to the file containing the function
        function_name: Name of the function being modified

    Returns:
        List of files and functions that would be affected
    """
    driver = get_driver()

    with driver.session() as session:
        result = session.run(
            """
            MATCH (changed:CodeNode)
            WHERE (changed.file = $file OR changed.file ENDS WITH $file)
              AND changed.name = $func
            MATCH (affected:CodeNode)-[:CALLS*1..5]->(changed)
            RETURN DISTINCT
                affected.file AS file,
                affected.name AS name,
                affected.line AS line,
                affected.type AS type
            ORDER BY affected.file, affected.line
            """,
            file=file_path,
            func=function_name,
        )

        affected = [dict(record) for record in result]

        # Group by file
        by_file = {}
        for item in affected:
            f = item["file"]
            if f not in by_file:
                by_file[f] = []
            by_file[f].append({"name": item["name"], "line": item["line"], "type": item["type"]})

        return {
            "changed": f"{file_path}:{function_name}",
            "affected_count": len(affected),
            "affected_files": len(by_file),
            "by_file": by_file,
        }


@mcp.tool()
def find_similar_code(description: str, top_k: int = 10) -> dict[str, Any]:
    """
    Find code similar to a natural language description.

    Uses keyword matching against symbol names.
    For better results, use specific technical terms.

    Args:
        description: Natural language description of what you're looking for
        top_k: Maximum number of results to return

    Returns:
        List of matching code symbols with file locations
    """
    driver = get_driver()
    top_k = min(max(top_k, 1), 50)  # Clamp to 1-50

    # Extract keywords from description
    keywords = [w.lower() for w in description.split() if len(w) > 2]

    with driver.session() as session:
        result = session.run(
            """
            MATCH (n:CodeNode)
            WHERE n.type IN ['function', 'class', 'struct', 'interface', 'trait']
              AND ANY(kw IN $keywords WHERE toLower(n.name) CONTAINS kw OR toLower(n.full_name) CONTAINS kw)
            RETURN n.file AS file,
                   n.name AS name,
                   n.full_name AS full_name,
                   n.line AS line,
                   n.type AS type
            LIMIT $k
            """,
            keywords=keywords,
            k=top_k,
        )

        matches = [dict(record) for record in result]

        return {"query": description, "keywords": keywords, "matches": matches, "count": len(matches)}


@mcp.tool()
def get_call_graph(entry_point: str, depth: int = 3) -> dict[str, Any]:
    """
    Get the call graph starting from an entry point.

    Args:
        entry_point: Name of the function/method to start from
        depth: How deep to traverse (1-5)

    Returns:
        Call graph as nodes and edges
    """
    depth = min(max(depth, 1), 5)
    driver = get_driver()

    with driver.session() as session:
        result = session.run(
            """
            MATCH (start:CodeNode)
            WHERE start.name = $entry OR start.full_name = $entry
            MATCH path = (start)-[:CALLS*1..$depth]->(called:CodeNode)
            WITH start, called, relationships(path) AS rels
            UNWIND rels AS rel
            WITH start, called, startNode(rel) AS from_node, endNode(rel) AS to_node
            RETURN DISTINCT
                from_node.name AS from_name,
                from_node.file AS from_file,
                to_node.name AS to_name,
                to_node.file AS to_file
            """,
            entry=entry_point,
            depth=depth,
        )

        edges = [dict(record) for record in result]

        # Build node set
        nodes = set()
        for edge in edges:
            nodes.add(edge["from_name"])
            nodes.add(edge["to_name"])

        return {"entry": entry_point, "depth": depth, "nodes": list(nodes), "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


@mcp.tool()
def search_symbols(pattern: str, symbol_type: str | None = None, limit: int = 20) -> dict[str, Any]:
    """
    Search for symbols by name pattern.

    Args:
        pattern: Pattern to search for (case-insensitive substring match)
        symbol_type: Optional filter by type (function, class, struct, etc.)
        limit: Maximum results to return

    Returns:
        List of matching symbols with locations
    """
    driver = get_driver()
    limit = min(max(limit, 1), 100)

    with driver.session() as session:
        if symbol_type:
            result = session.run(
                """
                MATCH (n:CodeNode)
                WHERE toLower(n.name) CONTAINS toLower($pattern)
                  AND n.type = $type
                RETURN n.name AS name,
                       n.full_name AS full_name,
                       n.type AS type,
                       n.file AS file,
                       n.line AS line
                ORDER BY n.name
                LIMIT $limit
                """,
                pattern=pattern,
                type=symbol_type,
                limit=limit,
            )
        else:
            result = session.run(
                """
                MATCH (n:CodeNode)
                WHERE toLower(n.name) CONTAINS toLower($pattern)
                RETURN n.name AS name,
                       n.full_name AS full_name,
                       n.type AS type,
                       n.file AS file,
                       n.line AS line
                ORDER BY n.name
                LIMIT $limit
                """,
                pattern=pattern,
                limit=limit,
            )

        matches = [dict(record) for record in result]

        return {"pattern": pattern, "type_filter": symbol_type, "matches": matches, "count": len(matches)}


@mcp.tool()
def get_file_structure(file_path: str) -> dict[str, Any]:
    """
    Get the structure of a specific file from the graph.

    Args:
        file_path: Path to the file (can be partial, will match ending)

    Returns:
        All symbols defined in the file
    """
    driver = get_driver()

    with driver.session() as session:
        result = session.run(
            """
            MATCH (n:CodeNode)
            WHERE n.file = $file OR n.file ENDS WITH $file
            RETURN n.name AS name,
                   n.full_name AS full_name,
                   n.type AS type,
                   n.file AS file,
                   n.line AS line,
                   n.end_line AS end_line
            ORDER BY n.line
            """,
            file=file_path,
        )

        symbols = [dict(record) for record in result]

        return {"file": file_path, "symbols": symbols, "count": len(symbols)}


@mcp.tool()
def get_graph_stats() -> dict[str, Any]:
    """
    Get statistics about the code graph.

    Returns:
        Statistics including node counts by type, file counts, etc.
    """
    driver = get_driver()

    with driver.session() as session:
        # Count by type
        type_counts = session.run(
            """
            MATCH (n:CodeNode)
            RETURN n.type AS type, count(*) AS count
            ORDER BY count DESC
            """
        )

        # Count files
        file_count = session.run(
            """
            MATCH (f:File)
            RETURN count(f) AS files
            """
        )

        # Count files by language
        lang_counts = session.run(
            """
            MATCH (f:File)
            WHERE f.language IS NOT NULL
            RETURN f.language AS language, count(*) AS count
            ORDER BY count DESC
            """
        )

        # Count all relationship types
        rel_counts = session.run(
            """
            MATCH ()-[r]->()
            WHERE type(r) IN ['CALLS', 'CONTAINS', 'INHERITS', 'IMPLEMENTS', 'USES', 'IMPORTS', 'DEFINES']
            RETURN type(r) AS rel_type, count(r) AS count
            ORDER BY count DESC
            """
        )

        # Count imports
        import_count = session.run(
            """
            MATCH (i:Import)
            RETURN count(i) AS imports
            """
        )

        types = {record["type"]: record["count"] for record in type_counts}
        files = file_count.single()["files"]
        languages = {record["language"]: record["count"] for record in lang_counts}
        relationships = {record["rel_type"]: record["count"] for record in rel_counts}
        imports = import_count.single()["imports"]

        return {
            "total_nodes": sum(types.values()),
            "by_type": types,
            "files_indexed": files,
            "by_language": languages,
            "relationships": relationships,
            "unique_imports": imports,
        }


def main():
    """Entry point for the code-graph MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
