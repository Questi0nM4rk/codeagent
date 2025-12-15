# code-graph-mcp

Code knowledge graph MCP server using Neo4j and Tree-sitter.
Based on research showing 75% improvement on code retrieval tasks.

## Features

- Parses code into AST using tree-sitter
- Stores code structure in Neo4j graph database
- Extracts relationships: CALLS, CONTAINS, INHERITS, IMPLEMENTS, USES
- Provides MCP tools for querying code dependencies

## Supported Languages

| Language | Extensions | Status |
|----------|------------|--------|
| C# | `.cs` | ✅ Full support |
| C/C++ | `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp` | ✅ Full support |
| Rust | `.rs` | ✅ Full support |
| Lua | `.lua` | ✅ Full support |
| Bash | `.sh`, `.bash`, `.zsh` | ✅ Full support |
| Python | `.py` | ✅ Full support |
| TypeScript | `.ts`, `.tsx` | ✅ Full support |
| JavaScript | `.js`, `.jsx` | ✅ Full support |
| Go | `.go` | ✅ Full support |

## Relationships Extracted

| Relationship | Description |
|--------------|-------------|
| `CALLS` | Function/method calls another function |
| `CONTAINS` | Parent contains child (class → method) |
| `INHERITS` | Class inherits from another class |
| `IMPLEMENTS` | Class implements interface/trait |
| `USES` | Code uses a type (field, parameter, return type) |
| `IMPORTS` | File imports a module |
| `DEFINES` | File defines a code entity |

## Installation

```bash
pip install -e .
```

## Usage

```bash
python -m code_graph_mcp.server
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `index_file` | Parse a file and add to knowledge graph |
| `index_directory` | Recursively index all files in a directory |
| `query_dependencies` | Find code dependencies for a symbol |
| `find_affected_by_change` | Find code affected by changes to a function |
| `find_similar_code` | Find code similar to a description |
| `get_call_graph` | Get call graph from an entry point |
| `search_symbols` | Search for symbols by name pattern |
| `get_file_structure` | Get structure of a file |
| `get_graph_stats` | Get statistics about the graph |

## Environment Variables

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=codeagent
```
