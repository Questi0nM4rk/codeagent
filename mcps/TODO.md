# MCP Development TODOs

## Current MCP Inventory

Based on `mcp-registry.json`:

| Category | MCP | Status | Notes |
|----------|-----|--------|-------|
| **Docker** | qdrant | ✅ Implemented | Vector store for Letta |
| **Docker** | neo4j | ✅ Implemented | Graph database for code-graph |
| **Docker** | letta | ✅ Implemented | Memory system (74% LOCOMO) |
| **NPM** | memory | ✅ Ready | Simple key-value memory |
| **NPM** | sequential-thinking | ✅ Ready | Reasoning chain |
| **NPM** | filesystem | ✅ Ready | File access |
| **NPM** | context7 | ✅ Ready | Library documentation |
| **NPM Optional** | github | ✅ Ready | Requires GITHUB_TOKEN |
| **NPM Optional** | tavily | ✅ Ready | Requires TAVILY_API_KEY |
| **Python** | code-graph | ✅ Implemented | AST-based code knowledge graph |
| **Python** | tot | ✅ Implemented | Tree-of-Thought reasoning |
| **Python** | reflection | ✅ Implemented | Self-reflection patterns |

---

## Completed Research

### Letta MCP Integration ✅

**Installation Architecture:**
- Dedicated installer: `mcps/installers/install-letta.sh`
- Delegates from `install-docker-mcps.sh`
- Handles Qdrant dependency automatically

**Key Findings:**
- Letta v0.15.1 uses built-in PostgreSQL (pgvector) for persistence
- External Qdrant optional for vector storage
- `letta-mcp-server` npm package connects to Letta API
- No auth required for localhost (`LETTA_PASSWORD` optional)

**Configuration:**
```bash
# MCP Registration
claude mcp add letta \
  --env "LETTA_BASE_URL=http://localhost:8283" \
  -- npx -y letta-mcp-server

# Health Check
curl http://localhost:8283/v1/health/
# Response: {"version":"0.15.1","status":"ok"}
```

**Environment Variables:**
- `OPENAI_API_KEY` - Required for embeddings (~$4/month for text-embedding-3-small)
- `LETTA_BASE_URL` - Set automatically to http://localhost:8283
- `LETTA_PASSWORD` - Optional, for remote/secured deployments

**Future Optimization:**
- Agent persistence configuration for session continuity
- Memory retention tuning (what to remember vs forget)
- Multi-agent patterns for complex code tasks

---

## Research Required

### High Priority

#### 1. code-graph MCP Enhancement ✅ COMPLETED
- **Current status**: ✅ Fully implemented (v0.2.0)
- **File**: `mcps/code-graph-mcp/src/code_graph_mcp/server.py`
- **Completed**:
  - ✅ Better Neo4j relationship types (INHERITS, IMPLEMENTS, USES, CONTAINS, DEFINES)
  - ✅ Cross-file dependency tracking via IMPORTS and USES relationships
  - ✅ Index optimization using UNWIND batch operations
  - ✅ Query patterns for common code analysis (all existing tools work)
- **Languages supported**: C#, C++, Rust, Lua, Bash, Python, TypeScript, JavaScript, Go (9 total)

#### 2. tot-mcp Enhancement ✅ COMPLETED
- **Current status**: ✅ Fully implemented (v0.2.0)
- **File**: `mcps/tot-mcp/src/tot_mcp/server.py`
- **Completed**:
  - ✅ Integration with Claude's thinking levels (auto-detected from problem complexity)
  - ✅ Persistent storage to `~/.codeagent/data/thought-trees/`
  - ✅ Advanced pruning (alpha-beta style, weighted criteria, diversity preservation)
  - ✅ New "diverse" strategy for exploring different solutions
  - ✅ New tools: `delete_tree`, `set_criteria_weights`
- **Reference**: https://arxiv.org/abs/2305.10601

#### 3. reflection-mcp Enhancement ✅ COMPLETED
- **Current status**: ✅ Fully implemented (v0.2.0)
- **File**: `mcps/reflection-mcp/src/reflection_mcp/server.py`
- **Completed**:
  - ✅ Persistent storage to `~/.codeagent/data/reflection-episodes/`
  - ✅ Lesson effectiveness tracking (`mark_lesson_effective`, `link_episode_to_lesson`)
  - ✅ Cross-session learning aggregation (`LessonPattern`, `_update_lesson_patterns`)
  - ✅ Export for learner skill (`export_lessons` tool)

### Medium Priority

#### 4. Neo4j Graph Schema ✅ COMPLETED
- **Init script**: `infrastructure/neo4j/init.cypher`
- **Completed**:
  - ✅ Constraints for unique identifiers (code_node_id, file_path, import_name)
  - ✅ Basic indexes for common lookups (name, full_name, type, file, line)
  - ✅ Composite indexes for query patterns (file+type, name+type, language)
  - ✅ Full-text search indexes (code_name_search, file_path_search, import_name_search)
  - ✅ Documentation of schema, relationships, and sample queries
  - ✅ Backup/restore scripts already implemented in `scripts/backup-memory.sh` and `scripts/restore-memory.sh`

#### 5. MCP Health Monitoring ✅ COMPLETED
- **CLI**: `bin/codeagent-status`
- **Config**: `config/monitoring.conf`
- **Completed**:
  - ✅ Continuous monitoring via `codeagent status --watch`
  - ✅ Auto-restart on failure with `--auto-restart` flag
  - ✅ Configurable alert thresholds with `--threshold N`
  - ✅ Log aggregation with service filtering: `codeagent logs [neo4j|qdrant|letta]`
  - ✅ JSON output for integration: `codeagent status --json`
  - ✅ Container stats (CPU, memory) in JSON output

### Low Priority

#### 6. Additional Tree-sitter Languages ✅ COMPLETED
- **Current**: C#, C++, Rust, Lua, Bash, Python, TypeScript, JavaScript, Go (9 languages)
- **Completed**:
  - ✅ Python (tree-sitter-python)
  - ✅ TypeScript (tree-sitter-typescript)
  - ✅ JavaScript (tree-sitter-javascript)
  - ✅ Go (tree-sitter-go)
- **Implementation**: Added to `pyproject.toml` and `install.sh`

---

## Implementation Notes

### Sub-installer Architecture

```
mcps/
├── install-mcps.sh             # Main orchestrator
├── mcp-registry.json           # Central registry
├── TODO.md                     # This file
├── installers/
│   ├── install-npm-mcps.sh     # NPM MCPs (npx-based)
│   ├── install-python-mcps.sh  # Custom Python MCPs
│   ├── install-docker-mcps.sh  # Docker orchestrator
│   └── install-letta.sh        # Letta-specific installer
├── code-graph-mcp/             # AST code analysis
├── tot-mcp/                    # Tree-of-Thought (placeholder)
└── reflection-mcp/             # Self-reflection (placeholder)
```

### Letta Installation Flow

```
install-docker-mcps.sh
    │
    ├── start_neo4j()           # Infrastructure only
    │
    └── install_letta()
            │
            └── install-letta.sh
                    ├── preflight_checks()
                    ├── start Qdrant (dependency)
                    ├── start Letta container
                    ├── wait for health
                    └── register MCP with Claude
```

### Testing Checklist

- [x] Letta health: `curl http://localhost:8283/v1/health/`
- [x] Letta MCP: `claude mcp list | grep letta`
- [x] NPM MCPs installer: `install-npm-mcps.sh` (all 4 required MCPs install)
- [x] Python MCPs installer: `install-python-mcps.sh` (all 3 MCPs install)
- [x] Docker MCPs installer: `install-docker-mcps.sh` (Neo4j + Letta healthy)
- [x] Force flag: `install-mcps.sh --force` (removes and reinstalls all MCPs)
- [x] Neo4j health: `curl http://localhost:7474`
- [ ] Fresh install: `rm -rf ~/.codeagent && ./install.sh`
- [ ] Update install: `./install.sh` (should skip existing)
- [ ] No-docker mode: `./install.sh --no-docker`

---

## Known Issues

1. **npx cold start**: First run of npx MCPs downloads packages (~5-10s delay)
2. **Docker startup**: Letta container needs ~30s to initialize
3. **Qdrant health check**: No curl in image, must use TCP port check
4. **Neo4j memory**: May need memory limits in docker-compose for large graphs
5. **OPENAI_API_KEY warning**: Shown if not configured, but Letta still starts

---

## References

- [MCP Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Claude Code MCP Docs](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [FastMCP Library](https://github.com/jlowin/fastmcp)
- [Letta Documentation](https://docs.letta.com/)
- [Letta MCP Server (npm)](https://github.com/oculairmedia/letta-mcp-server)
- [Tree-of-Thought Paper](https://arxiv.org/abs/2305.10601)
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)
