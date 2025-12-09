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
"""

import os
import logging
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        else:
            return None

        parser.language = lang
        _parsers[extension] = parser
        return parser
    except ImportError as e:
        logger.warning(f"Tree-sitter language not available for {extension}: {e}")
        return None


def extract_nodes(node, file_path: str, nodes: list | None = None, parent_name: str = ""):
    """Extract code nodes from AST."""
    if nodes is None:
        nodes = []

    # Map tree-sitter node types to our types
    type_map = {
        # C#
        "class_declaration": "class",
        "interface_declaration": "interface",
        "struct_declaration": "struct",
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
        # Rust
        "function_item": "function",
        "impl_item": "impl",
        "struct_item": "struct",
        "enum_item": "enum",
        "trait_item": "trait",
        "mod_item": "module",
        "use_declaration": "import",
        # Lua
        "function_declaration": "function",
        "local_function": "function",
        "function_call": "call",
        # Bash
        "function_definition": "function",
    }

    if node.type in type_map:
        name_node = node.child_by_field_name("name")
        name = name_node.text.decode() if name_node else f"anonymous_{node.start_point[0]}"

        full_name = f"{parent_name}.{name}" if parent_name else name

        nodes.append(
            {
                "id": f"{file_path}:{node.start_point[0]}:{name}",
                "type": type_map[node.type],
                "name": name,
                "full_name": full_name,
                "file": file_path,
                "line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
            }
        )

        # Update parent name for nested items
        if type_map[node.type] in ("class", "struct", "namespace", "module", "impl"):
            parent_name = full_name

    # Extract call relationships
    if node.type in ("call_expression", "invocation_expression", "function_call"):
        func_node = node.child_by_field_name("function") or node.child_by_field_name("name")
        if func_node:
            nodes.append(
                {
                    "id": f"{file_path}:{node.start_point[0]}:call",
                    "type": "call",
                    "name": func_node.text.decode(),
                    "file": file_path,
                    "line": node.start_point[0] + 1,
                    "caller": parent_name,
                }
            )

    for child in node.children:
        extract_nodes(child, file_path, nodes, parent_name)

    return nodes


def store_nodes_in_neo4j(nodes: list[dict], file_path: str):
    """Store extracted nodes in Neo4j."""
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

    if parser is None:
        return {"error": f"Unsupported file type: {extension}", "supported": [".cs", ".cpp", ".c", ".h", ".rs", ".lua", ".sh"]}

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = parser.parse(bytes(content, "utf8"))
        nodes = extract_nodes(tree.root_node, str(path))
        count = store_nodes_in_neo4j(nodes, str(path))

        return {
            "indexed": True,
            "file": str(path),
            "nodes_found": len(nodes),
            "nodes_stored": count,
            "types": list(set(n["type"] for n in nodes if n["type"] != "call")),
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

    supported = extensions or [".cs", ".cpp", ".cc", ".c", ".h", ".hpp", ".rs", ".lua", ".sh", ".bash"]
    results = {"indexed": 0, "failed": 0, "skipped": 0, "files": []}

    # Directories to skip
    skip_dirs = {"bin", "obj", "target", "node_modules", ".git", "__pycache__", "build", "dist"}

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
                results["files"].append({"file": str(path), "nodes": result.get("nodes_stored", 0)})

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
            MATCH (n:CodeNode)
            RETURN count(DISTINCT n.file) AS files
            """
        )

        # Count relationships
        rel_count = session.run(
            """
            MATCH ()-[r:CALLS]->()
            RETURN count(r) AS calls
            """
        )

        types = {record["type"]: record["count"] for record in type_counts}
        files = file_count.single()["files"]
        calls = rel_count.single()["calls"]

        return {"total_nodes": sum(types.values()), "by_type": types, "files_indexed": files, "call_relationships": calls}


def main():
    """Entry point for the code-graph MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
