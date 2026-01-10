# MCP Development TODOs

## Current MCP Inventory

Based on `mcp-registry.json`:

| Category | MCP | Status | Notes |
|----------|-----|--------|-------|
| **Docker** | qdrant | ✅ Implemented | Vector store for Letta |
| **Docker** | letta | ✅ Implemented | Memory system (74% LOCOMO) |
| **NPM** | context7 | ✅ Ready | Library documentation |
| **NPM Optional** | tavily | ✅ Ready | Requires TAVILY_API_KEY |
| **NPM Optional** | figma | ✅ Ready | Requires FIGMA_API_KEY |
| **NPM Optional** | supabase | ✅ Ready | Requires SUPABASE_ACCESS_TOKEN |
| **UVX** | code-execution | ✅ Ready | Sandboxed code execution (Docker) |
| **Python** | reflection | ✅ Implemented | Self-reflection patterns (+21% accuracy) |

### Removed MCPs
| MCP | Reason |
|-----|--------|
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

- [x] Letta health: `curl http://localhost:8283/v1/health/`
- [x] Letta MCP: `claude mcp list | grep letta`
- [x] Context7 MCP: `claude mcp list | grep context7`
- [x] Reflection MCP: `claude mcp list | grep reflection`
- [x] Docker MCPs installer: `install-docker-mcps.sh` (Qdrant + Letta healthy)
- [ ] Fresh install: `rm -rf ~/.codeagent && ./install.sh`
- [ ] Update install: `./install.sh` (should skip existing)
- [ ] No-docker mode: `./install.sh --no-docker`

---

## Known Issues

1. **npx cold start**: First run of npx MCPs downloads packages (~5-10s delay)
2. **Docker startup**: Letta container needs ~30s to initialize
3. **Qdrant health check**: No curl in image, must use TCP port check
4. **OPENAI_API_KEY warning**: Shown if not configured, but Letta still starts

---

## References

- [MCP Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Claude Code MCP Docs](https://docs.anthropic.com/en/docs/claude-code/mcp)
- [FastMCP Library](https://github.com/jlowin/fastmcp)
- [Letta Documentation](https://docs.letta.com/)
- [Reflexion Paper (NeurIPS 2023)](https://arxiv.org/abs/2303.11366)
