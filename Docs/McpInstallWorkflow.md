# MCP Installation Workflow

> Comprehensive design document for installing, configuring, and managing MCP servers in CodeAgent.
> This document uses **Letta** as the reference implementation. All other MCPs follow this same pattern.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [MCP Categories](#mcp-categories)
4. [Letta MCP Reference Implementation](#letta-mcp-reference-implementation)
5. [Installation Workflow](#installation-workflow)
6. [Script Design](#script-design)
7. [Configuration Files](#configuration-files)
8. [Health Check System](#health-check-system)
9. [Update and Force Reinstall](#update-and-force-reinstall)
10. [Error Handling](#error-handling)
11. [Testing Strategy](#testing-strategy)

---

## Overview

### Problem Statement

MCP (Model Context Protocol) servers require a consistent, repeatable installation process that:
- Works on fresh systems (first install)
- Updates existing installations (re-run without --force)
- Completely rebuilds from scratch (re-run with --force)
- Handles Docker containers, npm packages, Python packages, and Claude CLI registration
- Validates everything works before declaring success

### Goals

1. **Idempotent** - Running twice produces the same result
2. **Atomic** - Either everything succeeds or nothing changes
3. **Recoverable** - Failed installs can be retried
4. **Observable** - Clear logging of what's happening
5. **Extensible** - Easy to add new MCPs following the same pattern

### Non-Goals

- GUI installer
- Windows support (Linux/macOS only)
- Multiple simultaneous CodeAgent installations

---

## Architecture

### Directory Structure

```
~/.codeagent/
├── .env                          # API keys (Docker reads this)
├── infrastructure/
│   ├── docker-compose.yml        # All Docker services
│   └── configs/                  # Service-specific configs
│       ├── letta/
│       │   └── config.yaml       # Letta-specific config (if needed)
│       ├── neo4j/
│       │   └── init.cypher       # Neo4j initialization
│       └── qdrant/
│           └── config.yaml       # Qdrant config (if needed)
├── mcps/
│   ├── install-mcps.sh           # Main MCP installer (called by install.sh)
│   ├── mcp-registry.json         # Registry of all MCPs and their configs
│   └── custom/                   # Custom Python MCPs
│       ├── code-graph-mcp/
│       ├── tot-mcp/
│       └── reflection-mcp/
├── venv/                         # Python virtual environment
└── bin/                          # CLI commands
```

### Component Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         install.sh                               │
│  (entry point - handles args, calls sub-installers)             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     install-mcps.sh                              │
│  (orchestrates MCP installation based on mcp-registry.json)     │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ Docker MCPs   │      │  NPM MCPs     │      │ Python MCPs   │
│ (letta, neo4j │      │ (memory,      │      │ (code-graph,  │
│  qdrant)      │      │  sequential)  │      │  tot, reflect)│
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    claude mcp add/remove                         │
│  (registers MCPs with Claude Code CLI)                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## MCP Categories

MCPs fall into three categories based on their installation method:

### Category 1: Docker-Based MCPs

MCPs that run as Docker containers. Require:
- Docker image
- docker-compose service definition
- Health check endpoint
- Volume mounts for persistence
- Network connectivity

**Examples:**
- **Letta** - Memory system (requires Qdrant dependency)
- **Neo4j** - Graph database for code structure
- **Qdrant** - Vector store for embeddings

### Category 2: NPM-Based MCPs

MCPs installed via npm/npx. Require:
- Node.js and npm
- Package name and version
- Environment variables (if any)

**Examples:**
- `@modelcontextprotocol/server-memory` - Simple key-value memory
- `@modelcontextprotocol/server-sequential-thinking` - Reasoning
- `@modelcontextprotocol/server-filesystem` - File access
- `@upstash/context7-mcp` - Library documentation
- `letta-mcp-server` - Letta MCP client (connects to Docker Letta)

### Category 3: Python-Based MCPs (Custom)

Custom MCPs built for CodeAgent. Require:
- Python virtual environment
- pip install (editable mode)
- pyproject.toml with proper configuration

**Examples:**
- `code-graph-mcp` - Code knowledge graph
- `tot-mcp` - Tree-of-thought reasoning
- `reflection-mcp` - Self-reflection patterns

---

## Letta MCP Reference Implementation

Letta is the most complex MCP because it involves:
1. Docker container (letta/letta server)
2. Docker dependency (Qdrant for vectors)
3. NPM package (letta-mcp-server as the MCP client)
4. Environment variables (OPENAI_API_KEY, LETTA_BASE_URL)

### Letta Component Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code CLI                              │
│  (uses letta-mcp-server to communicate with Letta)              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ MCP Protocol (stdio)
┌─────────────────────────────────────────────────────────────────┐
│                   letta-mcp-server (NPM)                         │
│  Command: npx -y letta-mcp-server                               │
│  Env: LETTA_BASE_URL=http://localhost:8283                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ HTTP REST API
┌─────────────────────────────────────────────────────────────────┐
│                   Letta Server (Docker)                          │
│  Image: letta/letta:latest                                      │
│  Port: 8283                                                     │
│  Health: GET /v1/health/                                        │
│  Env: OPENAI_API_KEY (for embeddings)                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼ Qdrant Protocol (port 6333)
┌─────────────────────────────────────────────────────────────────┐
│                   Qdrant (Docker)                                │
│  Image: qdrant/qdrant:latest                                    │
│  Port: 6333 (REST), 6334 (gRPC)                                 │
│  Health: TCP port check (no curl in image)                      │
└─────────────────────────────────────────────────────────────────┘
```

### Letta Installation Requirements

| Requirement | Source | Notes |
|-------------|--------|-------|
| Docker | System | Must be installed and running |
| Qdrant container | docker-compose | Dependency - must start first |
| Letta container | docker-compose | Depends on healthy Qdrant |
| OPENAI_API_KEY | .env file | Required for embeddings |
| letta-mcp-server | npm | MCP client package |
| LETTA_BASE_URL | claude mcp add --env | Points to localhost:8283 |

### Letta Health Check Chain

```
1. Qdrant Health
   └─ Test: TCP connection to port 6333
   └─ Command: timeout 2 bash -c '</dev/tcp/localhost/6333'
   └─ Why: Qdrant image has no curl/wget for security

2. Letta Health
   └─ Test: HTTP GET /v1/health/
   └─ Command: curl -sf http://localhost:8283/v1/health/
   └─ Response: {"version":"X.X.X","status":"ok"}
   └─ Depends: Qdrant must be healthy first

3. MCP Health
   └─ Test: claude mcp list shows "letta: ✓ Connected"
   └─ Depends: Letta container must be healthy
```

### Letta Configuration Reference

**docker-compose.yml service:**
```yaml
letta:
  image: letta/letta:latest
  container_name: codeagent-letta
  ports:
    - "8283:8283"
  env_file:
    - path: ../.env
      required: false
  environment:
    LETTA_QDRANT_HOST: qdrant
    LETTA_QDRANT_PORT: 6333
    LETTA_LLM_EMBEDDING_MODEL: text-embedding-3-small
  volumes:
    - codeagent_letta_data:/root/.letta
  depends_on:
    qdrant:
      condition: service_healthy
  healthcheck:
    test: ["CMD-SHELL", "curl -sf http://localhost:8283/v1/health/ > /dev/null || exit 1"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s
  restart: unless-stopped
```

**Claude MCP registration:**
```bash
claude mcp add letta \
  --env "LETTA_BASE_URL=http://localhost:8283" \
  -- npx -y letta-mcp-server
```

---

## Installation Workflow

### Phase 1: Pre-flight Checks

Before installing any MCP:

```
1. Check system requirements
   ├─ Docker installed and running?
   ├─ Docker Compose v2 available?
   ├─ Node.js and npm installed?
   ├─ Python 3.10+ installed?
   └─ Claude Code CLI installed?

2. Check existing state
   ├─ Is this a fresh install or update?
   ├─ Are any Docker containers already running?
   ├─ Are any MCPs already registered?
   └─ Does .env file exist with required keys?

3. Determine installation mode
   ├─ --force flag? → Full reinstall (delete everything first)
   ├─ No flag, exists? → Update (only change what's needed)
   └─ No flag, fresh? → Fresh install
```

### Phase 2: Docker Infrastructure

For Docker-based MCPs:

```
1. Stop existing containers (if --force)
   └─ docker compose down --volumes (if --force)
   └─ docker compose down (if update)

2. Copy/update docker-compose.yml
   └─ Source: $SOURCE_DIR/infrastructure/docker-compose.yml
   └─ Dest: $INSTALL_DIR/infrastructure/docker-compose.yml

3. Start containers
   └─ docker compose up -d

4. Wait for health
   └─ Poll each container's health status
   └─ Timeout after 120 seconds
   └─ Fail if any container unhealthy
```

### Phase 3: NPM-Based MCPs

For each NPM MCP:

```
1. Remove existing registration (if --force)
   └─ claude mcp remove <name>

2. Register with Claude
   └─ claude mcp add <name> [--env KEY=VALUE] -- <command> <args>

3. Verify connection
   └─ Parse output of: claude mcp list
   └─ Check for "✓ Connected"
```

### Phase 4: Python-Based MCPs

For custom Python MCPs:

```
1. Ensure venv exists
   └─ python3 -m venv $INSTALL_DIR/venv

2. Install MCP SDK
   └─ $VENV/bin/pip install mcp

3. For each custom MCP:
   ├─ pip install -e $MCP_DIR (editable mode)
   ├─ claude mcp remove <name> (if --force)
   └─ claude mcp add <name> -- $VENV/bin/python -m <module>

4. Verify each MCP connects
```

### Phase 5: Verification

After all MCPs installed:

```
1. Run claude mcp list
2. Parse output for each expected MCP
3. Count connected vs failed
4. Report summary to user
5. Exit 0 if all connected, exit 1 if any failed
```

---

## Script Design

### Main Entry Point: install.sh

```bash
#!/bin/bash
# install.sh - Main CodeAgent installer

# Parse args
FORCE=false
NO_DOCKER=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --force|-f) FORCE=true; shift ;;
    --no-docker) NO_DOCKER=true; shift ;;
    *) shift ;;
  esac
done

# Export for sub-scripts
export CODEAGENT_FORCE=$FORCE
export CODEAGENT_NO_DOCKER=$NO_DOCKER

# ... other setup ...

# Call MCP installer
"$INSTALL_DIR/mcps/install-mcps.sh"
```

### MCP Installer: install-mcps.sh

The MCP installer should:

1. Read configuration from `mcp-registry.json`
2. Process MCPs in dependency order
3. Handle each category appropriately
4. Verify all MCPs at the end

**Pseudocode structure:**

```bash
#!/bin/bash
# install-mcps.sh

FORCE=${CODEAGENT_FORCE:-false}
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"

# Load MCP registry
# (In practice, parse JSON or use simple bash arrays)

# Phase 1: Docker MCPs
if [ "$CODEAGENT_NO_DOCKER" != "true" ]; then
  install_docker_mcps
fi

# Phase 2: NPM MCPs
install_npm_mcps

# Phase 3: Python MCPs
install_python_mcps

# Phase 4: Verify all
verify_all_mcps
```

### MCP Registry: mcp-registry.json

Central configuration for all MCPs:

```json
{
  "version": "1.0",
  "mcps": {
    "docker": [
      {
        "name": "qdrant",
        "container": "codeagent-qdrant",
        "healthcheck": {
          "type": "tcp",
          "port": 6333
        },
        "dependencies": []
      },
      {
        "name": "letta",
        "container": "codeagent-letta",
        "healthcheck": {
          "type": "http",
          "url": "http://localhost:8283/v1/health/"
        },
        "dependencies": ["qdrant"]
      },
      {
        "name": "neo4j",
        "container": "codeagent-neo4j",
        "healthcheck": {
          "type": "http",
          "url": "http://localhost:7474"
        },
        "dependencies": []
      }
    ],
    "npm": [
      {
        "name": "memory",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "env": {}
      },
      {
        "name": "sequential-thinking",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "env": {}
      },
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
        "env": {}
      },
      {
        "name": "letta",
        "command": "npx",
        "args": ["-y", "letta-mcp-server"],
        "env": {
          "LETTA_BASE_URL": "http://localhost:8283"
        },
        "requires_docker": ["letta"]
      }
    ],
    "python": [
      {
        "name": "code-graph",
        "module": "code_graph_mcp.server",
        "path": "mcps/custom/code-graph-mcp"
      },
      {
        "name": "tot",
        "module": "tot_mcp.server",
        "path": "mcps/custom/tot-mcp"
      },
      {
        "name": "reflection",
        "module": "reflection_mcp.server",
        "path": "mcps/custom/reflection-mcp"
      }
    ]
  }
}
```

---

## Configuration Files

### Required Environment Variables

Stored in `$INSTALL_DIR/.env`:

```bash
# Required for Letta embeddings
OPENAI_API_KEY=sk-...

# Optional - enables GitHub MCP
GITHUB_TOKEN=ghp_...

# Optional - enables Tavily web search
TAVILY_API_KEY=tvly-...
```

### Docker Compose Structure

Single `docker-compose.yml` with all Docker MCPs:

```yaml
services:
  # Dependency order matters - list dependencies first
  qdrant:
    # ... Qdrant config ...

  neo4j:
    # ... Neo4j config ...

  letta:
    # ... Letta config ...
    depends_on:
      qdrant:
        condition: service_healthy

volumes:
  # Named volumes for persistence
  codeagent_qdrant_data:
  codeagent_neo4j_data:
  codeagent_letta_data:

networks:
  default:
    name: codeagent-network
```

---

## Health Check System

### Health Check Types

**1. TCP Port Check (for containers without curl)**
```bash
health_check_tcp() {
  local host=$1
  local port=$2
  timeout 2 bash -c "</dev/tcp/$host/$port" 2>/dev/null
}
```

**2. HTTP Endpoint Check**
```bash
health_check_http() {
  local url=$1
  curl -sf "$url" > /dev/null 2>&1
}
```

**3. Docker Container Health**
```bash
health_check_container() {
  local container=$1
  local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null)
  [ "$status" = "healthy" ]
}
```

**4. MCP Connection Check**
```bash
health_check_mcp() {
  local name=$1
  claude mcp list 2>&1 | grep -q "$name:.*✓ Connected"
}
```

### Health Check Workflow

```
For each MCP:
  1. Determine health check type from registry
  2. Wait up to TIMEOUT seconds
  3. Poll every INTERVAL seconds
  4. If healthy → continue
  5. If timeout → log error, mark failed

At end:
  If any failed:
    Show failed MCPs
    Show troubleshooting commands
    Exit 1
  Else:
    Show success summary
    Exit 0
```

---

## Update and Force Reinstall

### Normal Update (no flags)

```
1. Check what's already installed
2. For Docker:
   - If containers running and healthy → skip
   - If containers unhealthy → restart
   - If containers missing → start
3. For NPM MCPs:
   - If already registered → skip
   - If not registered → add
4. For Python MCPs:
   - pip install -e (updates if changed)
   - If not registered → add
```

### Force Reinstall (--force flag)

```
1. Docker:
   - docker compose down --volumes --remove-orphans
   - Remove all codeagent_* volumes
   - docker compose up -d
   - Wait for health

2. NPM MCPs:
   - claude mcp remove <each>
   - claude mcp add <each>

3. Python MCPs:
   - pip install -e --force-reinstall
   - claude mcp remove <each>
   - claude mcp add <each>

4. Verify all from scratch
```

### Preserving Data

Even with --force:
- `.env` file is preserved (contains user's API keys)
- User is warned if volumes will be deleted
- Option to backup volumes first (future enhancement)

---

## Error Handling

### Error Categories

| Category | Example | Recovery |
|----------|---------|----------|
| Missing Dependency | Docker not installed | Exit with clear message |
| Network Error | Can't pull image | Retry with backoff |
| Health Timeout | Container won't start | Show logs, suggest fix |
| Registration Fail | claude mcp add fails | Show exact error |
| Permission Error | Can't write to dir | Suggest sudo or chmod |

### Error Messages

Every error should include:
1. What failed
2. Why it might have failed
3. How to fix it
4. Command to get more info

**Example:**
```
[ERROR] Letta container failed health check after 120 seconds

Possible causes:
  - OPENAI_API_KEY not set or invalid
  - Qdrant container not healthy
  - Port 8283 already in use

To investigate:
  docker logs codeagent-letta
  docker inspect codeagent-letta
  curl http://localhost:8283/v1/health/

To retry:
  codeagent start
```

### Rollback Strategy

If installation fails partway:
1. Log what was completed
2. Don't undo completed steps (idempotent design)
3. User can re-run to continue from where it failed
4. --force flag available for clean slate

---

## Testing Strategy

### Unit Tests

For each function:
- `health_check_tcp` - mock TCP connection
- `health_check_http` - mock curl response
- `parse_mcp_registry` - test JSON parsing

### Integration Tests

1. **Fresh Install Test**
   ```bash
   # Clean slate
   rm -rf ~/.codeagent
   docker volume rm $(docker volume ls -q | grep codeagent) 2>/dev/null

   # Install
   ./install.sh

   # Verify
   codeagent status
   claude mcp list
   ```

2. **Update Test**
   ```bash
   # Run install twice
   ./install.sh
   ./install.sh  # Should be fast, skip existing

   # Verify same result
   ```

3. **Force Reinstall Test**
   ```bash
   # Install, corrupt something, force reinstall
   ./install.sh
   docker stop codeagent-letta
   ./install.sh --force

   # Verify everything works
   ```

### Smoke Tests

Quick verification that core functionality works:
```bash
# After install, these should all work:
codeagent status           # Shows all services healthy
claude mcp list            # Shows all MCPs connected
curl localhost:8283/v1/health/  # Letta responds
curl localhost:7474        # Neo4j responds
```

---

## Appendix: Research Sources

### Letta Documentation
- [Letta MCP Setup Guide](https://docs.letta.com/guides/mcp/setup/)
- [Letta Docker Documentation](https://docs.letta.com/server/docker)
- [Letta Health Check API](https://docs.letta.com/api-reference/health/check)

### Letta MCP Server (NPM)
- [npm: letta-mcp-server](https://www.npmjs.com/package/letta-mcp-server)
- [GitHub: oculairmedia/Letta-MCP-server](https://github.com/oculairmedia/Letta-MCP-server)

### Letta Server (Docker)
- [GitHub: letta-ai/letta](https://github.com/letta-ai/letta)
- [compose.yaml](https://github.com/letta-ai/letta/blob/main/compose.yaml)
- [.env.example](https://github.com/letta-ai/letta/blob/main/.env.example)

### Qdrant
- [Qdrant Installation](https://qdrant.tech/documentation/guides/installation/)
- [Qdrant Health Check Issue](https://github.com/qdrant/qdrant/issues/4250)

### Key Technical Details

**Letta Server:**
- Image: `letta/letta:latest`
- Port: 8283
- Health endpoint: `GET /v1/health/`
- Response: `{"version":"X.X.X","status":"ok"}`
- Requires: OPENAI_API_KEY for embeddings

**Letta MCP Client:**
- Package: `letta-mcp-server`
- Command: `npx -y letta-mcp-server`
- Required env: `LETTA_BASE_URL=http://localhost:8283`

**Qdrant:**
- Image: `qdrant/qdrant:latest`
- Ports: 6333 (REST), 6334 (gRPC)
- Health: `/healthz` endpoint (but no curl in image)
- Workaround: TCP port check

---

## Next Steps

1. **Implement install-mcps.sh** following this design
2. **Create mcp-registry.json** with initial MCPs
3. **Test Letta flow** end-to-end
4. **Add remaining MCPs** one by one
5. **Add --force handling** for each category
6. **Write automated tests**
