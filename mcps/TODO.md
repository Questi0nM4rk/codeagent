# MCP Development TODOs

## Current MCP Inventory

Based on `mcp-registry.json`:

| Category | MCP | Status | Notes |
|----------|-----|--------|-------|
| **Docker** | qdrant | ✅ Implemented | Vector store for reflection |
| **Python** | amem | ✅ Implemented | Brain-like memory (NeurIPS 2025 A-MEM) |
| **NPM** | context7 | ✅ Ready | Library documentation |
| **NPM Optional** | tavily | ✅ Ready | Requires TAVILY_API_KEY |
| **NPM Optional** | figma | ✅ Ready | Requires FIGMA_API_KEY |
| **NPM Optional** | supabase | ✅ Ready | Requires SUPABASE_ACCESS_TOKEN |
| **UVX** | code-execution | ✅ Ready | Sandboxed code execution (Docker) |
| **Python** | reflection | ✅ Implemented | Self-reflection patterns (+21% accuracy) |

### Removed MCPs
| MCP | Reason |
|-----|--------|
| letta | Replaced with A-MEM (simpler, brain-like memory) |
| neo4j | code-graph removed - unreliable, not core to workflow |
| code-graph | Removed - AST parsing unreliable, wasted MCP calls |
| tot | Removed - Single use (architect only), replaced by ultrathink |
| sequential-thinking | Removed - Overlaps with Claude's native ultrathink |

---

## Active Development

### reflection-mcp Feedback Loop ✅ IMPLEMENTED
- **File**: `mcps/reflection-mcp/src/reflection_mcp/server.py`
- **Status**: All 11 tools now integrated across agents
- **Completed**:
  - ✅ Lesson effectiveness tracking (`mark_lesson_effective`, `link_episode_to_lesson`)
  - ✅ Cross-session learning (`export_lessons`, `get_common_lessons`)
  - ✅ Memory health monitoring (`get_episode_stats`, `clear_episodes`)
  - ✅ Task history lookup (`get_reflection_history`)

### Agent Integration
| Agent | New Tools |
|-------|-----------|
| implementer | `link_episode_to_lesson`, `mark_lesson_effective`, `get_reflection_history` |
| learner | `export_lessons`, `get_common_lessons` |
| reviewer | `get_common_lessons`, `store_episode` |
| researcher | `get_reflection_history` |
| validator | `get_episode_stats`, `clear_episodes` |

---

## Testing Checklist

- [x] A-MEM storage: `ls ~/.codeagent/memory/`
- [x] A-MEM MCP: `claude mcp list | grep amem`
- [x] Context7 MCP: `claude mcp list | grep context7`
- [x] Reflection MCP: `claude mcp list | grep reflection`
- [x] Qdrant health: `curl http://localhost:6333/healthz`
- [ ] Fresh install: `rm -rf ~/.codeagent && ./install.sh`
- [ ] Update install: `./install.sh` (should skip existing)
- [ ] No-docker mode: `./install.sh --no-docker`

---

## Known Issues

1. **npx cold start**: First run of npx MCPs downloads packages (~5-10s delay)
2. **Docker startup**: Qdrant container needs ~10s to initialize
3. **Qdrant health check**: No curl in image, must use TCP port check
4. **OPENAI_API_KEY warning**: Shown if not configured, A-MEM metadata generation will fail

---

## References

- [MCP Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Claude Code MCP Docs](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [FastMCP Library](https://github.com/jlowin/fastmcp)
- [A-MEM Paper (NeurIPS 2025)](https://github.com/agiresearch/A-mem)
- [Reflexion Paper (NeurIPS 2023)](https://arxiv.org/abs/2303.11366)
