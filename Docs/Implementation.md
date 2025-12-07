# Claude Code Co-Agent Stack

> Research-backed, accuracy-optimized autonomous coding system for .NET 10, C/C++, Rust, Lua, Bash

---

## Bypass Mode Philosophy

This system is designed for **full autonomous operation** without confirmation prompts.

### Why Bypass Mode?

- **Speed**: No interruptions for routine operations
- **Flow**: Agents execute complete workflows without stopping
- **Trust**: External validation catches errors, not permission prompts
- **Autonomy**: The system is smart enough to know when to proceed

### What Bypass Enables

```
✅ Read/Write/Edit any file
✅ Run any bash command
✅ Spawn subagents freely
✅ Query all MCPs
✅ Commit code automatically
✅ Run tests without asking
✅ Format code on save
```

### What's Still Protected (Self-Imposed Rules)

```
⚠️ Never git push without explicit request
⚠️ Never delete production data
⚠️ Never expose secrets in commits
⚠️ Never skip tests to "save time"
⚠️ Never self-validate (always use external tools)
```

### Trust Model

```
Permission prompts    →    External validation
(prevents mistakes)        (catches mistakes)

We trade pre-execution gates for post-execution verification.
This is faster AND more reliable (70-75% more errors caught).
```

---

## Architecture Decision Summary

| Decision               | Choice                                  | Why                                                             |
| ---------------------- | --------------------------------------- | --------------------------------------------------------------- |
| **Memory**             | Letta + Neo4j                           | 74% LOCOMO accuracy + 75% code retrieval improvement with graph |
| **Agent Pattern**      | Auto-detect sequential vs parallel      | System analyzes task and decides optimal execution path         |
| **Parallel Execution** | Subagents with file-level isolation     | Speed boost without context fragmentation                       |
| **Validation**         | External tools, not self-validation     | Catches 70-75% more errors than LLM self-review                 |
| **Reasoning**          | Tree-of-Thought + Self-Reflection       | +70% on complex reasoning, +21% on HumanEval                    |
| **Research Priority**  | Memory → Code Graph → Context7 → Tavily | Project context first, external fallback                        |
| **Thinking Levels**    | Per-agent parametrization               | Complex agents get "ultrathink", simple agents get "think"      |

---

## Thinking Level Strategy

Claude Code supports escalating thinking depth: `think` < `think hard` < `think harder` < `ultrathink`

Each agent is pre-configured with appropriate thinking level:

| Agent             | Thinking Level | Why                                              |
| ----------------- | -------------- | ------------------------------------------------ |
| **@researcher**   | `think hard`   | Synthesizing sources, not designing              |
| **@architect**    | `ultrathink`   | Most complex - exploring multiple solution paths |
| **@orchestrator** | `think harder` | Dependency analysis is complex but structured    |
| **@implementer**  | `think hard`   | TDD requires care but is procedural              |
| **@reviewer**     | `think hard`   | Systematic validation                            |
| **@learner**      | `think`        | Pattern extraction is straightforward            |

The thinking directive is injected into each agent's prompt automatically.

---

## Parallel Execution Model

### When Single-Agent (Sequential)

- Tasks share code/interfaces
- Changes in one area affect another
- Complex refactoring across modules
- Database migrations
- Shared state management

### When Multi-Agent (Parallel)

- Completely isolated features
- Different controllers/services with no shared code
- Independent modules (frontend vs backend)
- Separate microservices
- Tests for different features

### The Key Insight

Research says "don't use multi-agent for coding" specifically about **agents sharing context on the same code**. Parallel execution of **isolated tasks** is different — it's how human teams work.

```
❌ BAD: Two agents editing files that depend on each other
   Agent A: UserController.cs (uses JwtService)
   Agent B: AuthController.cs (modifies JwtService)
   → Context fragmentation, conflicts, inconsistencies

✅ GOOD: Two agents editing completely separate code
   Agent A: UserController.cs, UserService.cs, UserTests.cs
   Agent B: ProductController.cs, ProductService.cs, ProductTests.cs
   → No shared dependencies, just parallel speed
```

### Parallel Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        /plan-parallel                                │
│  Analyze task → Identify isolation boundaries → Define file locks   │
└─────────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│   Subagent A            │     │   Subagent B            │
│   (Claude Code spawn)   │     │   (Claude Code spawn)   │
│                         │     │                         │
│   Exclusive files:      │     │   Exclusive files:      │
│   - UserController      │     │   - ProductController   │
│   - UserService         │     │   - ProductService      │
│                         │     │                         │
│   Read-only (shared):   │     │   Read-only (shared):   │
│   - BaseController      │     │   - BaseController      │
│   - DbContext           │     │   - DbContext           │
└─────────────────────────┘     └─────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          /integrate                                  │
│  Merge → Full test suite → Interface check → Pattern consistency    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
~/.claude/
├── CLAUDE.md                    # Global preferences
├── settings.json                # Global MCP config
└── agents/                      # Reusable agents

project/
├── CLAUDE.md                    # Project-specific context
├── CLAUDE.local.md              # Local overrides (gitignored)
├── .claude/
│   ├── settings.json            # Project permissions & hooks
│   ├── agents/
│   │   ├── researcher.md
│   │   ├── architect.md
│   │   ├── implementer.md
│   │   ├── reviewer.md
│   │   └── learner.md
│   └── commands/
│       ├── scan.md
│       ├── plan.md
│       ├── implement.md
│       └── review.md
├── .mcp.json                    # Shared MCP servers
├── docker-compose.yml           # Infrastructure
└── docs/
    ├── architecture.md
    └── decisions/
```

---

## Infrastructure

### docker-compose.yml

```yaml
version: "3.8"

services:
  # Graph database for code structure
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474" # Browser
      - "7687:7687" # Bolt
    environment:
      NEO4J_AUTH: neo4j/codeagent
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: wget -qO- http://localhost:7474 || exit 1
      interval: 10s
      timeout: 5s
      retries: 5

  # Vector store for Letta
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  # Memory system
  letta:
    image: letta/letta:latest
    ports:
      - "8283:8283"
    environment:
      LETTA_QDRANT_HOST: qdrant
      LETTA_QDRANT_PORT: 6333
    volumes:
      - letta_data:/root/.letta
    depends_on:
      - qdrant

  # Local embeddings (optional, saves API costs)
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  neo4j_data:
  qdrant_data:
  letta_data:
  ollama_data:
```

### Start Infrastructure

```bash
# Start services
docker-compose up -d

# Pull embedding model (if using Ollama)
docker exec ollama ollama pull mxbai-embed-large

# Verify
curl http://localhost:8283/health  # Letta
curl http://localhost:6333/health  # Qdrant
curl http://localhost:7474         # Neo4j
```

---

## MCP Server Stack

### Installation

```bash
#!/bin/bash
# install-mcps.sh

# ============================================
# CORE - Always needed
# ============================================
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem $PWD
claude mcp add git -- npx -y @modelcontextprotocol/server-git --repository $PWD
claude mcp add github --env GITHUB_TOKEN=$GITHUB_TOKEN -- npx -y @modelcontextprotocol/server-github
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory

# ============================================
# REASONING - For complex tasks
# ============================================
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking

# ============================================
# MEMORY & KNOWLEDGE
# ============================================
# Letta (primary memory - 74% LOCOMO)
claude mcp add letta -- npx -y @letta-ai/mcp-server

# Code Graph (75% retrieval improvement)
# Requires custom setup - see Custom MCPs section
claude mcp add code-graph -- python -m code_graph_mcp.server

# ============================================
# RESEARCH - Priority order
# ============================================
# 1. Documentation (free, always current)
claude mcp add context7 -- npx -y @upstash/context7-mcp

# 2. Structured research (best for agents)
claude mcp add tavily --env TAVILY_API_KEY=$TAVILY_API_KEY -- npx -y tavily-mcp

# 3. Direct URL fetch
claude mcp add fetch -- npx -y @anthropic/mcp-fetch

# ============================================
# LANGUAGE SERVERS (your stack)
# ============================================
# .NET / C#
claude mcp add omnisharp -- npx -y mcp-lsp-bridge --server omnisharp --args "-lsp"

# C/C++
claude mcp add clangd -- npx -y mcp-lsp-bridge --server clangd

# Rust
claude mcp add rust-analyzer -- npx -y mcp-lsp-bridge --server rust-analyzer

# Lua
claude mcp add lua-language-server -- npx -y mcp-lsp-bridge --server lua-language-server

# ============================================
# VALIDATION
# ============================================
claude mcp add semgrep -- npx -y @semgrep/mcp-server

# ============================================
# CUSTOM - To be built (see Custom MCPs section)
# ============================================
# claude mcp add tot -- python -m tot_mcp.server
# claude mcp add reflection -- python -m reflection_mcp.server
```

### .mcp.json (Project-level, committed)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-git", "--repository", "."]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

---

## Agents

### .claude/agents/researcher.md

```markdown
---
name: researcher
description: Gathers context from memory and external sources. ALWAYS invoke before implementation.
tools: Read, Grep, Glob, Bash, letta, code-graph, context7, tavily, fetch
model: sonnet
thinking: think hard
permissions: bypass
---

# Researcher Agent

Think hard about this research task.

You are a research specialist. Your job is to gather ALL relevant context before any work begins.

## Permissions (Bypass Mode)

- **Read**: All files without confirmation
- **Grep/Glob**: Full search capabilities
- **Bash**: grep, find, cat, head, tail, wc, tree
- **MCPs**: letta, code-graph, context7, tavily, fetch
- **Auto-execute**: All research operations without asking

## Research Priority (STRICT ORDER)

1. **Project Memory First**
   - Query Letta: similar past implementations, patterns, decisions
   - Query code-graph: affected files, dependencies, call chains
2. **Codebase Analysis**

   - Find all files touching the feature area
   - Map function dependencies
   - Note existing patterns and conventions

3. **External Research (only if memory insufficient)**
   - Context7 for library/framework docs
   - Tavily for best practices, security patterns
   - Fetch for specific URLs

## Output Format
```

## Context Summary

### From Memory

- [relevant past decisions]
- [similar implementations]

### Affected Code

- file:line - description
- file:line - description

### Dependencies

- [call graph summary]

### External Research (if needed)

- [best practices found]

### Confidence: X/10

### Knowledge Gaps: [list any unknowns]

```

## Rules
- NEVER skip memory lookup
- ALWAYS report confidence score
- If confidence < 7, flag for human review
- Return structured findings, not prose
- Execute searches immediately, don't ask permission
```

### .claude/agents/architect.md

```markdown
---
name: architect
description: Designs solutions using Tree-of-Thought reasoning. Invoke for complex tasks.
tools: Read, Grep, Glob, Bash, sequential-thinking, code-graph, letta, tot
model: sonnet
thinking: ultrathink
permissions: bypass
---

# Architect Agent

Ultrathink about this design problem. Take your time to explore multiple approaches thoroughly.

You design solutions by exploring multiple approaches before committing.

## Permissions (Bypass Mode)

- **Read**: All files without confirmation
- **Grep/Glob**: Full search capabilities
- **Bash**: tree, find, grep (for codebase exploration)
- **MCPs**: sequential-thinking, code-graph, letta, tot
- **Auto-execute**: All design exploration without asking

## Process

### 1. Problem Decomposition

Break the task into independent sub-problems.

### 2. Tree-of-Thought Exploration

For each sub-problem:

- Generate 3 candidate approaches
- Evaluate each: feasibility (1-10), risk (1-10), complexity (1-10)
- Prune approaches scoring < 6 on any dimension
- Select best path or backtrack if all fail

### 3. Design Output
```

## Architecture Decision

### Problem Statement

[one sentence]

### Explored Approaches

1. [approach] - Score: X/10 - [why selected/rejected]
2. [approach] - Score: X/10 - [why selected/rejected]
3. [approach] - Score: X/10 - [why selected/rejected]

### Selected Design

[detailed design]

### Files to Modify

- path/file.cs - [what changes]

### Files to Create

- path/newfile.cs - [purpose]

### Test Strategy

- [what to test]
- [edge cases]

### Risks

- [risk] → [mitigation]

```

## Rules
- NEVER jump to first solution
- ALWAYS explore at least 3 approaches
- Use sequential-thinking MCP for complex logic
- Query code-graph for impact analysis
- Store decision rationale in Letta
- Execute exploration immediately, don't ask permission
```

### .claude/agents/implementer.md

```markdown
---
name: implementer
description: Implements code using TDD. Full autonomous execution.
tools: Read, Write, Edit, Bash, Grep, Glob, Task, code-graph, letta, git
model: sonnet
thinking: think hard
permissions: bypass
---

# Implementer Agent

Think hard about this implementation. Follow TDD strictly.

You write code using strict Test-Driven Development.

## Permissions (Bypass Mode)

- **Read/Write/Edit**: All files without confirmation
- **Bash**: ALL commands without confirmation
- **Grep/Glob**: Full search capabilities
- **Task**: Spawn test runners, linters
- **Git**: commit, add, status, diff (not push)
- **MCPs**: filesystem, git, code-graph, letta, language servers
- **Auto-execute**: Everything except git push

## Auto-Execute Behaviors

- Run tests immediately after writing
- Format code automatically after write
- Commit on test success without asking
- Run linters in background
- Update code-graph on file changes

## TDD Loop (MANDATORY)
```

1. WRITE TEST → 2. RUN TEST (must fail) → 3. COMMIT TEST
   ↓
2. WRITE CODE → 5. RUN TEST → 6. PASS? → NO → back to 4
   ↓ ↓
   YES MAX 3 ATTEMPTS → flag for help
   ↓
3. COMMIT CODE → 8. REFACTOR (optional) → 9. NEXT TEST

````

## Language-Specific Commands

### .NET
```bash
# Test
dotnet test --filter "FullyQualifiedName~TestName"

# Build
dotnet build --warnaserror

# Format (auto-runs on save via hook)
dotnet format

# Commit
git add -A && git commit -m "feat: description"
````

### C/C++

```bash
# Build
cmake --build build --parallel

# Test
ctest --test-dir build --output-on-failure

# Lint
clang-tidy src/*.cpp -- -std=c++23

# Format (auto-runs on save via hook)
clang-format -i file.cpp
```

### Rust

```bash
# Test
cargo test

# Build
cargo build

# Lint
cargo clippy -- -D warnings

# Format (auto-runs on save via hook)
cargo fmt
```

### Lua

```bash
# Test
busted --verbose

# Lint
luacheck .

# Format (auto-runs on save via hook)
stylua .
```

## Commit Message Format

```
type(scope): description

Types: feat, fix, refactor, test, docs, chore
Examples:
- feat(auth): add JWT refresh token support
- fix(user): handle null email validation
- test(order): add edge case for empty cart
```

## Rules

- NEVER write implementation before tests
- NEVER modify tests to make them pass
- ALWAYS run tests after each change
- MAX 3 attempts per failing test, then escalate
- Follow patterns from code-graph and Letta
- Update Letta with new patterns learned
- COMMIT automatically when tests pass
- DON'T ask for permission, just execute

````

### .claude/agents/reviewer.md

```markdown
---
name: reviewer
description: Validates code independently. Uses external tools, not self-review.
tools: Read, Bash, Grep, Glob, semgrep, code-graph, letta
model: sonnet
thinking: think hard
permissions: bypass
---

# Reviewer Agent

Think hard about this review. Be thorough and systematic.

You validate code using external tools. NEVER rely on self-assessment.

## Permissions (Bypass Mode)
- **Read**: All files without confirmation
- **Bash**: ALL validation commands without confirmation
- **Grep/Glob**: Full search capabilities
- **MCPs**: semgrep, code-graph, letta
- **Auto-execute**: All validation tools immediately

## Auto-Execute Behaviors
- Run all linters immediately
- Run security scans immediately
- Run full test suite immediately
- Query memory for pattern matching
- DON'T wait for confirmation

## Validation Pipeline (ALL MUST PASS)

### 1. Static Analysis
```bash
# .NET
dotnet format --verify-no-changes
dotnet build --warnaserror

# C/C++
clang-tidy src/*.cpp -- -std=c++23
cppcheck --enable=all --error-exitcode=1 src/

# Rust
cargo clippy -- -D warnings
cargo audit

# Lua
luacheck .
````

### 2. Security Scan

```bash
semgrep --config auto --error .
```

### 3. Test Execution

```bash
# Run full test suite
# .NET: dotnet test
# Rust: cargo test
# C++: ctest --test-dir build
# Lua: busted
# Must achieve 100% pass rate
```

### 4. Memory Consistency

- Query Letta: "Does this match project conventions?"
- Query code-graph: "Any broken dependencies?"

### 5. Requirements Check

- Compare implementation against /plan output
- Verify all acceptance criteria met

## Output Format

```
## Review Results

### Static Analysis
- [ ] Format check: PASS/FAIL
- [ ] Build warnings: PASS/FAIL (list issues)
- [ ] Linting: PASS/FAIL (list issues)

### Security
- [ ] Semgrep: PASS/FAIL (list findings)

### Tests
- [ ] All tests pass: YES/NO
- [ ] Coverage: X%

### Consistency
- [ ] Matches project patterns: YES/NO
- [ ] No broken dependencies: YES/NO

### Requirements
- [ ] All criteria met: YES/NO
- [ ] Missing: [list]

## VERDICT: APPROVED / CHANGES REQUIRED

### Required Changes (if any)
1. file:line - issue - fix
2. file:line - issue - fix
```

## Rules

- NEVER approve based on "looks good"
- ALWAYS run all validation tools
- If any check fails, return CHANGES REQUIRED
- Be specific: file, line, issue, fix
- Execute all validations immediately, don't ask

````

### .claude/agents/orchestrator.md

```markdown
---
name: orchestrator
description: Analyzes tasks for parallel execution and manages subagent spawning.
tools: Read, Grep, Glob, Bash, Task, code-graph, letta
model: sonnet
thinking: think harder
permissions: bypass
---

# Orchestrator Agent

Think harder about this parallelization analysis. Carefully map all dependencies.

You analyze tasks for parallel execution potential and coordinate subagents.

## Permissions (Bypass Mode)
- **Read**: All files without confirmation
- **Grep/Glob**: Full search capabilities
- **Bash**: ALL commands for dependency analysis
- **Task**: Spawn subagents without confirmation
- **MCPs**: code-graph, letta
- **Auto-execute**: Dependency analysis and subagent spawning

## Auto-Execute Behaviors
- Query code-graph immediately
- Analyze dependencies without asking
- Spawn subagents when parallel is safe
- Don't ask for confirmation on parallelization decision

## Core Responsibility
Determine if a task can be safely parallelized and manage the execution.

## Isolation Analysis Process

### 1. Dependency Mapping
For each proposed subtask:
````

Query code-graph:

- What files will this task modify?
- What do those files import/depend on?
- What other files import/depend on them?

```

### 2. Conflict Detection
```

For each pair of subtasks (A, B):
files_A = files modified by A
files_B = files modified by B
deps_A = dependencies of files_A
deps_B = dependencies of files_B

If (files_A ∩ files_B) ≠ ∅ → CONFLICT (same files)
If (files_A ∩ deps_B) ≠ ∅ → CONFLICT (A modifies B's dependency)
If (deps_A ∩ files_B) ≠ ∅ → CONFLICT (B modifies A's dependency)

Else → SAFE TO PARALLELIZE

```

### 3. Output Format

```

## Parallel Execution Plan

### Parallelizable: YES/NO

### Task Breakdown

#### Task A: [name]

Exclusive files (can modify):

- path/to/file1.cs
- path/to/file2.cs

Read-only files (can read, cannot modify):

- path/to/shared.cs

Forbidden files (do not touch):

- path/to/unrelated.cs

#### Task B: [name]

Exclusive files (can modify):

- path/to/other1.cs
- path/to/other2.cs

Read-only files (can read, cannot modify):

- path/to/shared.cs

### Shared Code (LOCKED - no task may modify)

- path/to/shared.cs
- path/to/interfaces/

### Execution Order

1. Parallel: Task A, Task B
2. Sequential (after parallel): Integration tests

### Integration Requirements

- Run full test suite
- Verify interface contracts
- Check for pattern drift

````

## Subagent Spawning

When spawning subagents, provide each with:

1. **Task-specific prompt** with exclusive/read-only/forbidden file lists
2. **Isolated context** - only knowledge relevant to their task
3. **No cross-communication** - subagents don't talk to each other
4. **Completion signal** - report back when done
5. **Bypass permissions** - subagents also run in bypass mode

## Subagent Prompt Template

```markdown
# Parallel Task: ${TASK_NAME}

Think hard about this implementation.

## Permissions (Bypass Mode)
You have full autonomous access. Execute without asking.

## File Boundaries (CRITICAL)
✅ EXCLUSIVE (modify freely): ${EXCLUSIVE_FILES}
📖 READ-ONLY (read only): ${READONLY_FILES}
🚫 FORBIDDEN (don't touch): ${FORBIDDEN_FILES}

## Rules
1. NEVER modify outside EXCLUSIVE list
2. If need to change read-only → STOP, report violation
3. TDD: test first, max 3 attempts
4. Commit on success
````

## Rules

- NEVER parallelize if ANY file conflicts detected
- When in doubt, recommend sequential execution
- Always include integration step after parallel work
- Shared interfaces must be defined BEFORE parallel execution starts
- Execute analysis immediately, don't ask for permission

````

### .claude/agents/learner.md

```markdown
---
name: learner
description: Post-task learning. Auto-activates after /implement and /review.
tools: Read, Grep, letta, code-graph
model: haiku
thinking: think
permissions: bypass
---

# Learner Agent

Think about what patterns can be extracted from this task.

You extract and store learnings after each task.

## Permissions (Bypass Mode)
- **Read**: All files without confirmation
- **Grep**: Search capabilities
- **MCPs**: letta, code-graph
- **Auto-execute**: Pattern extraction and storage silently

## Auto-Execute Behaviors
- Extract patterns immediately after task completion
- Store in Letta without confirmation
- Update code-graph silently
- Run in background, don't interrupt workflow

## Triggers
- After successful /implement
- After successful /review
- On explicit /learn command

## Learning Extraction

### 1. Pattern Recognition
- What patterns were used?
- Any new patterns introduced?
- What worked well?

### 2. Error Analysis
- What errors occurred?
- How were they fixed?
- Prevention strategies?

### 3. Decision Documentation
- Key decisions made
- Alternatives considered
- Rationale for choices

## Storage Format

### To Letta (Semantic Memory)
````

{
"type": "pattern",
"context": "authentication",
"pattern": "JWT with refresh token rotation",
"files": ["src/Auth/JwtService.cs"],
"learned_from": "task-123",
"confidence": 0.9
}

```

### To Code-Graph (Structural Memory)
```

{
"type": "dependency",
"from": "AuthController",
"to": "JwtService",
"relationship": "uses"
}

```

## Rules
- Extract patterns, not just facts
- Include confidence scores
- Link to source files
- Tag by domain for retrieval
- Execute silently, don't interrupt user
```

---

## Commands

### .claude/commands/scan.md

```markdown
---
command: /scan
description: Build complete knowledge of codebase
allowed-tools: Read, Glob, Grep, Bash, code-graph, letta
permissions: bypass
auto-execute: true
---

# /scan - Build Knowledge Base

Scans entire codebase and builds knowledge graph + memory.

**Runs fully autonomously.** No confirmations needed.

## Usage
```

/scan # Scan current directory
/scan src/ # Scan specific path
/scan --full # Force full rescan

````

## Process

### 1. Discovery
```bash
find . -type f \( \
  -name "*.cs" -o \
  -name "*.cpp" -o -name "*.c" -o -name "*.h" -o \
  -name "*.rs" -o \
  -name "*.lua" -o \
  -name "*.sh" -o -name "*.zsh" \
\) ! -path "*/bin/*" ! -path "*/obj/*" ! -path "*/target/*"
````

### 2. AST Parsing (via code-graph MCP)

For each file:

- Extract: namespaces, classes, functions, structs
- Map: imports, dependencies, call relationships
- Store in Neo4j

### 3. Pattern Extraction (via Letta)

- Coding conventions used
- Architecture patterns
- Test patterns
- Error handling patterns

### 4. Completeness Report

```
## Scan Complete

### Coverage
- Files scanned: X
- Functions indexed: X
- Dependencies mapped: X

### By Language
- C#: X files, X functions
- C++: X files, X functions
- Rust: X files, X functions
- Lua: X files, X functions

### Patterns Detected
- [pattern]: [files using it]

### Knowledge Gaps
- [areas with sparse coverage]

### Completeness: X%
```

## Post-Scan

- Invoke @learner to store patterns
- Update CLAUDE.md with discovered architecture

````

### .claude/commands/plan.md

```markdown
---
command: /plan
description: Research, design, and automatically detect if parallel execution is possible
allowed-tools: Read, Grep, Glob, Bash, letta, code-graph, context7, tavily, sequential-thinking, tot
agents: researcher, architect, orchestrator
permissions: bypass
auto-parallel: true
auto-execute: true
---

# /plan - Unified Planning (Auto-Detects Parallel)

Gathers context, designs solution, and automatically determines if parallel execution is beneficial.

**Runs fully autonomously.** Invokes agents without confirmation.

## Usage
````

/plan "Add JWT authentication" # Auto-detect execution mode
/plan "Add users, products, and orders" # Will detect parallelizable
/plan --sequential "Complex refactoring" # Force sequential
/plan --deep "Investigate performance issue" # Extra research phase

```

## Process

### Phase 1: Research (@researcher) [think hard]
1. Query Letta for similar past work
2. Query code-graph for affected areas
3. If needed: Context7 for docs, Tavily for best practices
4. Output: Context Summary with confidence score

### Phase 2: Design (@architect) [ultrathink]
1. Decompose into sub-problems
2. Generate 3+ approaches per sub-problem
3. Evaluate and select best path
4. Output: Architecture Decision document

### Phase 3: Parallelization Analysis (@orchestrator) [think harder]
**Automatically runs if task has multiple subtasks**

1. For each subtask, map:
   - Files that will be modified
   - Dependencies of those files
   - Files that depend on those files

2. Conflict detection:
```

For each pair of subtasks (A, B):
files_A = files modified by A
files_B = files modified by B
deps_A = dependencies of files_A
deps_B = dependencies of files_B

     If (files_A ∩ files_B) ≠ ∅ → CONFLICT
     If (files_A ∩ deps_B) ≠ ∅ → CONFLICT
     If (deps_A ∩ files_B) ≠ ∅ → CONFLICT

     Else → PARALLELIZABLE

```

3. Decision:
- **SEQUENTIAL**: Single subtask, conflicts detected, or --sequential flag
- **PARALLEL**: Multiple subtasks, no conflicts, estimated speedup > 30%

### Phase 4: Output Plan

## Output (Sequential Mode)
```

## Plan: [Task Name]

### Execution Mode: SEQUENTIAL

Reason: [single task / conflicts in X files / user requested]

### Research Summary

[from @researcher]

### Architecture Decision

[from @architect]

### Implementation Order

1. [ ] Step 1 - [files]
2. [ ] Step 2 - [files]

### Test Strategy

- Unit tests for: [list]
- Integration tests for: [list]

### Confidence: X/10

Ready for /implement

```

## Output (Parallel Mode)
```

## Plan: [Task Name]

### Execution Mode: PARALLEL ⚡

Reason: 3 independent subtasks, no file conflicts
Estimated speedup: 65% (5 min vs 15 min)

### Research Summary

[from @researcher]

### Architecture Decision

[from @architect]

### Parallelization Analysis

[from @orchestrator]

#### Task A: [name]

Exclusive files: [list]
Read-only: [list]
Forbidden: [list]

#### Task B: [name]

Exclusive files: [list]
Read-only: [list]
Forbidden: [list]

### Shared Code (LOCKED)

- [files no task may modify]

### Pre-Implementation Requirements

1. [ ] Define shared interfaces (if any)
2. [ ] Define shared DTOs (if any)

### Confidence: X/10

Ready for /implement (will auto-parallelize)

```

## Auto-Detection Rules

| Condition | Result |
|-----------|--------|
| Single subtask | Sequential |
| `--sequential` flag | Sequential |
| Any file modified by 2+ subtasks | Sequential |
| Subtask A modifies dependency of B | Sequential |
| All subtasks fully isolated | Parallel |
| Estimated speedup < 30% | Sequential (overhead not worth it) |
```

````

### .claude/commands/implement.md

```markdown
---
command: /implement
description: Execute plan using TDD (auto-detects parallel from plan)
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, code-graph, letta, Task, git
agents: implementer, orchestrator
permissions: bypass
pre-hook: verify-plan-exists
post-hook: invoke-learner
auto-parallel: true
auto-execute: true
auto-commit: true
---

# /implement - TDD Implementation (Auto-Parallel)

Implements the plan using TDD. Automatically uses parallel execution if the plan detected isolated subtasks.

**Runs fully autonomously.** Writes, tests, and commits without confirmation.

## Usage
````

/implement # Execute plan (auto-detects mode from /plan)
/implement --sequential # Force sequential even if plan allows parallel
/implement --step 2 # Start from step 2 (sequential mode)
/implement --continue # Continue from last checkpoint

```

## Auto-Execute Behaviors
- Write tests immediately
- Run tests immediately
- Format code on save (via hooks)
- Commit on success (with conventional commit)
- Spawn subagents for parallel tasks
- DON'T ask for any confirmations

## Mode Detection

Reads the plan from Letta and checks `Execution Mode`:
- If `SEQUENTIAL` → Single-agent TDD loop
- If `PARALLEL` → Spawn subagents for isolated tasks

## Sequential Mode Process

### 1. Load Plan
- Retrieve plan from Letta
- Verify all prerequisites met

### 2. TDD Loop (per step) [think hard]
```

For each step in plan:

1. Write test file
2. Run test → must fail
3. Commit test (auto)
4. Write implementation
5. Run test → must pass
6. If fail: fix (max 3 attempts)
7. If still fail: checkpoint, escalate
8. Commit implementation (auto)
9. Run full test suite
10. If regression: rollback, fix

```

### 3. Validation & Commit
- Run language-specific linter (auto via hooks)
- Run full test suite
- Commit with conventional commit message (auto)

## Parallel Mode Process

### 1. Load Parallel Plan
- Retrieve plan with task boundaries from Letta
- Verify shared contracts defined (if required)

### 2. Spawn Subagents [think harder for orchestration]
For each isolated task, spawn a Claude Code subagent:

```

## Subagent prompt template:

You are implementing: ${TASK_NAME}

Think hard about this implementation.

YOUR EXCLUSIVE FILES (you may modify):
${EXCLUSIVE_FILES}

READ-ONLY FILES (you may read but NOT modify):
${READONLY_FILES}

FORBIDDEN FILES (do not access):
${FORBIDDEN_FILES}

RULES:

1. TDD: Write tests first
2. Only modify YOUR EXCLUSIVE files
3. If you need to change read-only → STOP and report
4. Max 3 attempts per failing test

---

```

### 3. Monitor & Collect
- Track each subagent's progress
- Detect boundary violations
- Collect completion reports

### 4. Auto-Integration
After all subagents complete:
- Verify no conflicts (should be none)
- Run full test suite
- Check interface consistency
- If any failure → report which task caused it

## Output (Sequential)
```

## Implementation Complete

### Mode: SEQUENTIAL

### Steps Completed

- [x] Step 1: [description]
- [x] Step 2: [description]

### Files Modified

- path/file.cs (created/modified)

### Tests Added

- path/TestFile.cs

### Test Results

- All tests: PASS
- Coverage: X%

Ready for /review

```

## Output (Parallel)
```

## Implementation Complete

### Mode: PARALLEL ⚡

Duration: 5m 23s (vs ~15m sequential)

### Task Results

#### Task A: User Management ✅

Files modified: 4
Tests added: 12
Boundary violations: None

#### Task B: Product Catalog ✅

Files modified: 4
Tests added: 15
Boundary violations: None

### Integration

- Merge conflicts: None
- Full test suite: 27/27 passing
- Interface consistency: ✅

Ready for /review

```

## Failure Handling

### Sequential
- Max 3 attempts per failing test
- On failure: create checkpoint, report blocker
- Human can `/implement --continue` after fix

### Parallel
- Boundary violation → Stop that subagent, report issue
- Test failure in one task → Other tasks continue
- Integration failure → Report which task(s) caused it
- Can re-run single task: `/implement --task=A`
```

### .claude/commands/review.md

```markdown
---
command: /review
description: Validate implementation against requirements
allowed-tools: Read, Bash, Grep, Glob, semgrep, code-graph, letta
agents: reviewer
permissions: bypass
post-hook: invoke-learner-on-pass
auto-execute: true
---

# /review - Validation

Independent validation using external tools.

**Runs fully autonomously.** Executes all validation without confirmation.

## Usage
```

/review # Review current changes
/review --security # Extra security focus
/review --performance # Include perf analysis

````

## Auto-Execute Behaviors
- Run all linters immediately
- Run security scan immediately
- Run full test suite immediately
- Query memory for pattern consistency
- DON'T ask, just validate

## Process

### 1. Static Analysis
```bash
# Language-specific linting
dotnet format --verify-no-changes
cargo clippy -- -D warnings
clang-tidy src/*.cpp
luacheck .
````

### 2. Security Scan

```bash
semgrep --config auto --error .
```

### 3. Test Verification

```bash
# Full test suite
dotnet test
cargo test
ctest --test-dir build
busted
```

### 4. Memory Consistency

- Compare with patterns in Letta
- Check code-graph for orphaned dependencies

### 5. Requirements Match

- Load original /plan
- Verify each requirement met

## Output

```
## Review Results

### Checks
| Check | Status | Issues |
|-------|--------|--------|
| Format | ✅ PASS | - |
| Build | ✅ PASS | - |
| Lint | ⚠️ WARN | 2 warnings |
| Security | ✅ PASS | - |
| Tests | ✅ PASS | 47/47 |
| Patterns | ✅ PASS | - |
| Requirements | ✅ PASS | 5/5 |

### Warnings (non-blocking)
- file:line - warning message

### VERDICT: ✅ APPROVED

### Post-Review
- Learnings stored in Letta
- Ready for commit/PR
```

## Failure Handling

- Any FAIL → return CHANGES REQUIRED
- List specific fixes needed
- Do NOT approve with unresolved issues

````

### .claude/commands/integrate.md

```markdown
---
command: /integrate
description: Integrate parallel work and validate consistency (auto-triggers after parallel /implement)
allowed-tools: Read, Bash, Grep, Glob, semgrep, code-graph, letta
agents: reviewer
permissions: bypass
thinking: think hard
auto-triggers: after /implement when mode=PARALLEL
auto-execute: true
---

# /integrate - Parallel Integration

Validates and integrates work from parallel implementation.

**Auto-triggers when /implement completes in PARALLEL mode.** Runs fully autonomously.

## Usage
````

/integrate # Usually auto-triggered
/integrate --skip-tests # Skip test run (not recommended)
/integrate --verbose # Detailed output

````

## Process

### 1. Merge Validation
```bash
# Should be conflict-free since files are isolated
git status
git diff --stat
````

### 2. Full Test Suite

```bash
# Run ALL tests, not just new ones
dotnet test --verbosity normal
cargo test
ctest --test-dir build
busted
```

### 3. Interface Contract Validation

Check that parallel implementations agree on:

- Shared interface signatures
- DTO structures
- Database schema assumptions
- API contracts

```
Query code-graph:
- Do all implementations of IUserService match the interface?
- Are all DTOs used consistently?
- Any type mismatches across boundaries?
```

### 4. Pattern Consistency Check

Query Letta:

- Does Task A's code follow same patterns as Task B?
- Any style drift between parallel implementations?
- Naming conventions consistent?

### 5. Dependency Verification

```
Query code-graph:
- Any circular dependencies introduced?
- Any orphaned code (written but not called)?
- Any missing implementations?
```

### 6. Security Scan

```bash
semgrep --config auto --error .
```

## Output

```
## Integration Results

### Merge Status
Conflicts: NONE ✅
Files changed: 24
Lines added: 847
Lines removed: 12

### Test Results
Total tests: 156
Passed: 156 ✅
Failed: 0
Coverage: 84%

### Contract Validation
Interface consistency: ✅ PASS
DTO consistency: ✅ PASS
Schema consistency: ✅ PASS

### Pattern Consistency
Naming conventions: ✅ PASS
Error handling: ⚠️ WARN - Task B uses exceptions, Task A uses Result<T>
Logging: ✅ PASS

### Dependency Check
Circular dependencies: NONE ✅
Orphaned code: NONE ✅
Missing implementations: NONE ✅

### Security
Semgrep findings: 0 ✅

## VERDICT: ✅ INTEGRATION SUCCESSFUL

### Warnings (non-blocking)
1. Pattern drift in error handling - consider standardizing

### Ready for /review
```

## Failure Handling

### Test Failures

```
INTEGRATION FAILED: Test failures

Failing tests:
- UserServiceTests.CreateUser_WithInvalidEmail_ReturnsError
  Reason: Task A expects ValidationException, shared code returns Result.Failure

Root cause: Contract mismatch between Task A and shared validation

Resolution options:
1. Update Task A to use Result<T> pattern
2. Update shared validation to throw exceptions
3. Add adapter in Task A

Recommendation: Option 1 (matches project patterns)
```

### Contract Mismatch

```
INTEGRATION FAILED: Contract mismatch

IUserService.CreateUser:
- Shared interface: Task<Result<UserDTO>> CreateUser(CreateUserRequest)
- Task A implementation: Task<UserDTO> CreateUser(CreateUserRequest)

Resolution: Task A must update return type to match interface
```

### Pattern Drift

```
INTEGRATION WARNING: Pattern drift detected

Error handling:
- Task A: Uses Result<T> monad (3 files)
- Task B: Uses exceptions (4 files)
- Project standard: Result<T> (from CLAUDE.md)

Recommendation: Refactor Task B to use Result<T>
Priority: MEDIUM (code works but inconsistent)
```

````

---

## CLAUDE.md Template

### ~/.claude/CLAUDE.md (Global)

```markdown
# Global Claude Configuration

## Identity
Senior software engineer. Direct communication. No fluff.

## Principles
1. Accuracy over speed - verify before acting
2. Test-first development - always TDD
3. Memory-first research - check Letta before web search
4. External validation - never self-review code

## Languages
Primary: C# (.NET 10), C++23, C, Rust, Lua
Shell: Bash, Zsh
Editor: Neovim

## Response Style
- Concise, technical
- Code over prose
- Show commands, not just describe
- Include file:line references
````

### project/CLAUDE.md (Project-level)

````markdown
# Project: [Name]

## Stack

- .NET 10 / C# 13
- Target: net10.0

## Commands

```bash
# Build
dotnet build --warnaserror

# Test
dotnet test --verbosity normal

# Format
dotnet format

# Run
dotnet run --project src/App
```
````

## Architecture

@docs/architecture.md

## Key Directories

- src/Core/ - Domain logic, no external dependencies
- src/Infrastructure/ - External integrations (DB, APIs)
- src/Api/ - HTTP endpoints
- tests/ - Test projects mirror src/ structure

## Conventions

- Primary constructors for DI
- `Span<T>` for performance-critical paths
- XML docs on all public APIs
- No `var` for non-obvious types
- Nullable reference types enabled

## Patterns in Use

- CQRS with MediatR
- Repository pattern for data access
- Result<T> for error handling (no exceptions for flow control)

## Past Decisions

@docs/decisions/

````

---

## Settings & Hooks

### .claude/settings.json (Full Bypass Mode)

For autonomous operation with full permissions:

```json
{
  "permissions": {
    "allow": [
      "Read(*)",
      "Write(*)",
      "Edit(*)",
      "Bash(*)",
      "Grep(*)",
      "Glob(*)",
      "Task(*)",
      "WebFetch(*)",
      "mcp__letta(*)",
      "mcp__code-graph(*)",
      "mcp__context7(*)",
      "mcp__tavily(*)",
      "mcp__sequential-thinking(*)",
      "mcp__tot(*)",
      "mcp__reflection(*)",
      "mcp__semgrep(*)",
      "mcp__filesystem(*)",
      "mcp__git(*)",
      "mcp__github(*)"
    ],
    "deny": []
  },

  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(git commit:*)",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-commit.sh"
          }
        ]
      },
      {
        "matcher": "Bash(git push:*)",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/pre-push.sh"
          }
        ]
      }
    ],

    "PostToolUse": [
      {
        "matcher": "Write(*.cs)",
        "hooks": [
          {
            "type": "command",
            "command": "dotnet format --include \"$CLAUDE_FILE\" 2>/dev/null || true"
          }
        ]
      },
      {
        "matcher": "Write(*.rs)",
        "hooks": [
          {
            "type": "command",
            "command": "cargo fmt 2>/dev/null || true"
          }
        ]
      },
      {
        "matcher": "Write(*.cpp|*.c|*.h|*.hpp)",
        "hooks": [
          {
            "type": "command",
            "command": "clang-format -i \"$CLAUDE_FILE\" 2>/dev/null || true"
          }
        ]
      },
      {
        "matcher": "Write(*.lua)",
        "hooks": [
          {
            "type": "command",
            "command": "stylua \"$CLAUDE_FILE\" 2>/dev/null || true"
          }
        ]
      },
      {
        "matcher": "Write(*.sh)",
        "hooks": [
          {
            "type": "command",
            "command": "shfmt -w \"$CLAUDE_FILE\" 2>/dev/null || true"
          }
        ]
      },
      {
        "matcher": "Write(*.json)",
        "hooks": [
          {
            "type": "command",
            "command": "jq '.' \"$CLAUDE_FILE\" > \"$CLAUDE_FILE.tmp\" && mv \"$CLAUDE_FILE.tmp\" \"$CLAUDE_FILE\" 2>/dev/null || true"
          }
        ]
      }
    ]
  },

  "env": {
    "CODEAGENT_MODE": "autonomous",
    "CODEAGENT_THINKING": "enabled",
    "TDD_STRICT": "true",
    "EXTERNAL_VALIDATION_ONLY": "true"
  }
}
````

### .claude/hooks/ Directory

Create these hook scripts for command-level automation:

#### .claude/hooks/pre-commit.sh

```bash
#!/bin/bash
# Pre-commit hook - runs before any git commit

set -e

echo "🔍 Running pre-commit checks..."

# Detect language and run appropriate checks
if [ -f "*.csproj" ] || [ -d "obj" ]; then
    echo "  → .NET: Running tests..."
    dotnet test --no-build --verbosity quiet || exit 1
fi

if [ -f "Cargo.toml" ]; then
    echo "  → Rust: Running tests..."
    cargo test --quiet || exit 1
fi

if [ -f "CMakeLists.txt" ] || [ -f "Makefile" ]; then
    echo "  → C/C++: Running tests..."
    if [ -d "build" ]; then
        ctest --test-dir build --output-on-failure || exit 1
    fi
fi

if [ -f "*.rockspec" ] || [ -d "spec" ]; then
    echo "  → Lua: Running tests..."
    busted --quiet || exit 1
fi

echo "✅ Pre-commit checks passed"
```

#### .claude/hooks/pre-push.sh

```bash
#!/bin/bash
# Pre-push hook - runs before any git push

set -e

echo "🔍 Running pre-push checks..."

# Security scan
if command -v semgrep &> /dev/null; then
    echo "  → Security scan..."
    semgrep --config auto --error --quiet . || {
        echo "❌ Security issues found. Fix before pushing."
        exit 1
    }
fi

# Full test suite
echo "  → Full test suite..."
if [ -f "*.csproj" ]; then
    dotnet test --verbosity quiet || exit 1
elif [ -f "Cargo.toml" ]; then
    cargo test --quiet || exit 1
elif [ -f "CMakeLists.txt" ]; then
    ctest --test-dir build --output-on-failure || exit 1
fi

echo "✅ Pre-push checks passed"
```

#### .claude/hooks/post-implement.sh

```bash
#!/bin/bash
# Post-implement hook - runs after /implement completes

echo "📝 Post-implementation tasks..."

# Update code graph
if command -v codeagent &> /dev/null; then
    echo "  → Updating code graph..."
    # Trigger incremental scan of modified files
    git diff --name-only HEAD~1 | xargs -I {} codeagent index {}
fi

# Store patterns in memory
echo "  → Extracting patterns for memory..."
# Learner agent is auto-triggered, this is backup

echo "✅ Post-implementation complete"
```

### CLAUDE.md Permission Block

Add this to CLAUDE.md for full autonomous operation:

```markdown
## Permissions

This project runs in **full autonomous mode**. You have unrestricted access to:

### Tools (All Allowed)

- **Read/Write/Edit**: All files without confirmation
- **Bash**: All commands without confirmation
- **Grep/Glob**: Full search capabilities
- **Task**: Spawn subagents freely
- **WebFetch**: Access external URLs
- **All MCPs**: Full access to all configured MCP servers

### Autonomous Behaviors

- Execute tests without asking
- Commit code when tests pass
- Run linters and formatters automatically
- Spawn parallel subagents when beneficial
- Query memory and code graph freely
- Search external documentation as needed

### What NOT to Do (Self-Imposed)

- Never push to main/master without explicit request
- Never delete production data
- Never expose secrets in commits
- Never skip tests to "save time"
- Never self-validate (always use external tools)

### Environment

- Mode: Autonomous
- Thinking: Enabled (per-agent levels)
- TDD: Strict enforcement
- Validation: External only
```

---

## Comprehensive Hooks Reference

### Hook Types

| Type            | Trigger                  | Use Case                           |
| --------------- | ------------------------ | ---------------------------------- |
| **PreToolUse**  | Before tool executes     | Validation, reminders, checks      |
| **PostToolUse** | After tool executes      | Formatting, indexing, logging      |
| **PreCommand**  | Before /command runs     | Load context, verify prerequisites |
| **PostCommand** | After /command completes | Cleanup, learning, notifications   |

### Language-Specific Hooks

#### .NET (C#)

```json
{
  "PostToolUse": [
    {
      "matcher": "Write(*.cs)",
      "hooks": [
        {
          "type": "command",
          "command": "dotnet format --include \"$CLAUDE_FILE\""
        },
        {
          "type": "command",
          "command": "dotnet build --no-restore -v q 2>&1 | head -20"
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash(dotnet test:*)",
      "hooks": [
        { "type": "command", "command": "dotnet build --no-restore -v q" }
      ]
    }
  ]
}
```

#### Rust

```json
{
  "PostToolUse": [
    {
      "matcher": "Write(*.rs)",
      "hooks": [
        { "type": "command", "command": "cargo fmt" },
        { "type": "command", "command": "cargo check 2>&1 | head -30" }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash(cargo test:*)",
      "hooks": [{ "type": "command", "command": "cargo build --quiet" }]
    }
  ]
}
```

#### C/C++

```json
{
  "PostToolUse": [
    {
      "matcher": "Write(*.cpp|*.c|*.h|*.hpp)",
      "hooks": [
        { "type": "command", "command": "clang-format -i \"$CLAUDE_FILE\"" },
        {
          "type": "command",
          "command": "clang-tidy \"$CLAUDE_FILE\" -- -std=c++20 2>&1 | head -20"
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "Bash(ctest:*)",
      "hooks": [
        { "type": "command", "command": "cmake --build build --parallel" }
      ]
    }
  ]
}
```

#### Lua

```json
{
  "PostToolUse": [
    {
      "matcher": "Write(*.lua)",
      "hooks": [
        { "type": "command", "command": "stylua \"$CLAUDE_FILE\"" },
        {
          "type": "command",
          "command": "luacheck \"$CLAUDE_FILE\" 2>&1 | head -20"
        }
      ]
    }
  ]
}
```

### Command-Level Hooks

These run before/after slash commands:

```json
{
  "commands": {
    "/scan": {
      "pre": [".claude/hooks/backup-memory.sh"],
      "post": [".claude/hooks/notify-scan-complete.sh"]
    },
    "/plan": {
      "pre": [".claude/hooks/load-context.sh"],
      "post": [".claude/hooks/save-plan.sh"]
    },
    "/implement": {
      "pre": [".claude/hooks/verify-plan-exists.sh"],
      "post": [".claude/hooks/post-implement.sh"]
    },
    "/review": {
      "pre": [".claude/hooks/ensure-tests-exist.sh"],
      "post": [".claude/hooks/generate-report.sh"]
    }
  }
}
```

### Safety Hooks (Even in Bypass Mode)

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash(rm -rf:*)",
      "hooks": [
        {
          "type": "command",
          "command": "echo '⚠️  Destructive command detected. Proceeding...' && sleep 1"
        }
      ]
    },
    {
      "matcher": "Bash(*DROP TABLE*|*DELETE FROM*:*)",
      "hooks": [
        {
          "type": "command",
          "command": "echo '⚠️  Database destructive operation. Double-checking...'"
        }
      ]
    },
    {
      "matcher": "Write(*.env|*secrets*|*credentials*)",
      "hooks": [
        {
          "type": "command",
          "command": ".claude/hooks/check-no-secrets.sh \"$CLAUDE_FILE\""
        }
      ]
    }
  ]
}
```

### Git Workflow Hooks

```json
{
  "PreToolUse": [
    {
      "matcher": "Bash(git commit:*)",
      "hooks": [{ "type": "command", "command": ".claude/hooks/pre-commit.sh" }]
    },
    {
      "matcher": "Bash(git push:*)",
      "hooks": [{ "type": "command", "command": ".claude/hooks/pre-push.sh" }]
    },
    {
      "matcher": "Bash(git checkout main|git checkout master:*)",
      "hooks": [
        {
          "type": "command",
          "command": "echo '⚠️  Switching to protected branch'"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Bash(git commit:*)",
      "hooks": [
        {
          "type": "command",
          "command": "echo '✅ Committed:' && git log -1 --oneline"
        }
      ]
    }
  ]
}
```

### Memory & Learning Hooks

```json
{
  "PostToolUse": [
    {
      "matcher": "Write(*.cs|*.rs|*.cpp|*.lua)",
      "hooks": [
        {
          "type": "command",
          "command": ".claude/hooks/index-file.sh \"$CLAUDE_FILE\""
        }
      ]
    }
  ]
}
```

#### .claude/hooks/index-file.sh

```bash
#!/bin/bash
# Index modified file into code graph

FILE="$1"

if [ -z "$FILE" ]; then
    exit 0
fi

# Call code-graph MCP to index (if running)
if curl -s http://localhost:3100/health > /dev/null 2>&1; then
    curl -X POST http://localhost:3100/index \
        -H "Content-Type: application/json" \
        -d "{\"file\": \"$FILE\"}" \
        > /dev/null 2>&1
fi
```

---

## Agent Permission Blocks

Each agent should include explicit permission acknowledgment:

### @researcher Permissions

```markdown
## Permissions

- Read: All files
- Grep/Glob: Full search
- MCPs: letta, code-graph, context7, tavily, fetch
- Bash: grep, find, cat, head, tail
- Mode: Bypass (no confirmation needed)
```

### @architect Permissions

```markdown
## Permissions

- Read: All files
- Grep/Glob: Full search
- MCPs: sequential-thinking, code-graph, letta, tot
- Bash: tree, find, grep
- Mode: Bypass (no confirmation needed)
```

### @orchestrator Permissions

```markdown
## Permissions

- Read: All files
- Grep/Glob: Full search
- Task: Spawn subagents
- MCPs: code-graph, letta
- Bash: All (for dependency analysis)
- Mode: Bypass (no confirmation needed)
```

### @implementer Permissions

```markdown
## Permissions

- Read/Write/Edit: All files
- Bash: ALL (full access)
- MCPs: filesystem, git, code-graph, letta, language servers
- Task: Spawn test runners
- Mode: Bypass (no confirmation needed)

## Auto-Execute

- Run tests without asking
- Format code automatically
- Commit on success
- Run linters after write
```

### @reviewer Permissions

```markdown
## Permissions

- Read: All files
- Bash: ALL (for running validation tools)
- MCPs: semgrep, code-graph, letta
- Mode: Bypass (no confirmation needed)

## Auto-Execute

- Run all linters
- Run all tests
- Run security scans
- Check memory consistency
```

### @learner Permissions

```markdown
## Permissions

- Read: All files
- MCPs: letta, code-graph
- Mode: Bypass (no confirmation needed)

## Auto-Execute

- Extract patterns without asking
- Store in memory automatically
- Update code graph silently
```

---

## Custom MCPs to Build

These provide the highest research-backed accuracy improvements:

### 1. Tree-of-Thought MCP (+70% on complex reasoning)

```python
# tot_mcp/server.py
"""
Tree-of-Thought MCP Server

Enables systematic exploration of solution paths with backtracking.
Based on ToT paper showing 4% → 74% improvement on Game of 24.
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import json

server = Server("tot-mcp")

# State management
thought_tree = {}
current_node = "root"

@server.tool()
async def generate_thoughts(
    problem: str,
    num_candidates: int = 3,
    context: str = ""
) -> list[dict]:
    """
    Generate N candidate next steps for the current problem.

    Returns list of {id, thought, rationale} objects.
    """
    # In production: call Claude to generate candidates
    # For now: return structure for main agent to fill
    return {
        "instruction": f"Generate {num_candidates} distinct approaches to: {problem}",
        "format": [
            {"id": "thought_1", "approach": "...", "rationale": "..."},
            {"id": "thought_2", "approach": "...", "rationale": "..."},
            {"id": "thought_3", "approach": "...", "rationale": "..."}
        ],
        "context": context
    }

@server.tool()
async def evaluate_thoughts(
    thoughts: list[dict],
    criteria: list[str] = ["feasibility", "risk", "complexity"]
) -> list[dict]:
    """
    Evaluate each thought against criteria.

    Returns thoughts with scores and classification (sure/maybe/impossible).
    """
    return {
        "instruction": "Score each thought 1-10 on each criterion",
        "criteria": criteria,
        "classification_rules": {
            "sure": "All scores >= 7",
            "maybe": "Any score 4-6",
            "impossible": "Any score <= 3"
        },
        "thoughts": thoughts
    }

@server.tool()
async def select_path(
    evaluated_thoughts: list[dict],
    strategy: str = "greedy"  # greedy, beam, sampling
) -> dict:
    """
    Select best thought(s) to pursue based on strategy.
    """
    return {
        "instruction": f"Using {strategy} strategy, select path(s) to pursue",
        "evaluated": evaluated_thoughts,
        "strategies": {
            "greedy": "Pick highest scoring 'sure' thought",
            "beam": "Keep top 3 'sure' or 'maybe' thoughts",
            "sampling": "Probabilistically sample based on scores"
        }
    }

@server.tool()
async def backtrack(reason: str) -> dict:
    """
    Current path failed. Return to previous decision point.
    """
    return {
        "action": "backtrack",
        "reason": reason,
        "instruction": "Mark current path as 'impossible', return to parent node, try next candidate"
    }

if __name__ == "__main__":
    server.run()
```

### 2. Self-Reflection MCP (+21% on HumanEval)

```python
# reflection_mcp/server.py
"""
Self-Reflection MCP Server

Implements Reflexion pattern with episodic memory.
Based on NeurIPS 2023 paper showing 67% → 88% on HumanEval.
"""

from mcp.server import Server
from mcp.types import Tool
import json
from datetime import datetime

server = Server("reflection-mcp")

# Episodic memory store (in production: use Letta or vector DB)
episodes = []

@server.tool()
async def reflect_on_output(
    output: str,
    feedback: str,
    feedback_type: str = "test_failure"  # test_failure, lint_error, review_comment
) -> dict:
    """
    Generate verbal reflection on output given feedback.

    Returns structured reflection for storage.
    """
    return {
        "instruction": "Analyze why the output failed and what to do differently",
        "output_summary": output[:500],
        "feedback": feedback,
        "feedback_type": feedback_type,
        "reflection_format": {
            "what_went_wrong": "...",
            "root_cause": "...",
            "what_to_try_next": "...",
            "general_lesson": "..."
        }
    }

@server.tool()
async def store_episode(
    task: str,
    approach: str,
    outcome: str,  # success, failure
    reflection: dict,
    code_context: str = ""
) -> dict:
    """
    Store episode in episodic memory for future retrieval.
    """
    episode = {
        "id": len(episodes),
        "timestamp": datetime.now().isoformat(),
        "task": task,
        "approach": approach,
        "outcome": outcome,
        "reflection": reflection,
        "code_context": code_context[:1000]
    }
    episodes.append(episode)
    return {"stored": True, "episode_id": episode["id"]}

@server.tool()
async def retrieve_similar_episodes(
    current_task: str,
    current_error: str = "",
    top_k: int = 3
) -> list[dict]:
    """
    Retrieve similar past episodes for learning.

    In production: use vector similarity search.
    """
    return {
        "instruction": f"Find {top_k} most relevant past episodes",
        "current_task": current_task,
        "current_error": current_error,
        "episodes": episodes[-10:],  # Simple: return recent
        "usage": "Apply lessons from past reflections to current task"
    }

@server.tool()
async def generate_improved_attempt(
    original_output: str,
    reflection: dict,
    similar_episodes: list[dict]
) -> dict:
    """
    Generate improved attempt incorporating reflection and past lessons.
    """
    return {
        "instruction": "Generate improved solution using reflection insights",
        "original": original_output[:500],
        "key_insight": reflection.get("what_to_try_next"),
        "past_lessons": [e.get("reflection", {}).get("general_lesson") for e in similar_episodes],
        "requirement": "Address root cause, don't just patch symptoms"
    }

if __name__ == "__main__":
    server.run()
```

### 3. Code-Graph MCP (75% retrieval improvement)

```python
# code_graph_mcp/server.py
"""
Code Graph MCP Server

AST-based code knowledge graph using Neo4j.
Based on research showing 75% improvement on code retrieval.
"""

from mcp.server import Server
from mcp.types import Tool
from neo4j import GraphDatabase
import tree_sitter_c_sharp as ts_csharp
import tree_sitter_cpp as ts_cpp
import tree_sitter_rust as ts_rust
from tree_sitter import Language, Parser

server = Server("code-graph-mcp")

# Neo4j connection
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "codeagent"))

# Tree-sitter parsers
PARSERS = {
    ".cs": Parser(Language(ts_csharp.language())),
    ".cpp": Parser(Language(ts_cpp.language())),
    ".c": Parser(Language(ts_cpp.language())),
    ".rs": Parser(Language(ts_rust.language())),
}

@server.tool()
async def index_file(file_path: str, content: str) -> dict:
    """
    Parse file and add to knowledge graph.

    Extracts: classes, functions, imports, calls.
    """
    ext = "." + file_path.split(".")[-1]
    parser = PARSERS.get(ext)

    if not parser:
        return {"error": f"Unsupported file type: {ext}"}

    tree = parser.parse(bytes(content, "utf8"))

    # Extract nodes (simplified - real impl walks full AST)
    nodes = extract_nodes(tree.root_node, file_path)

    # Store in Neo4j
    with driver.session() as session:
        for node in nodes:
            session.run("""
                MERGE (n:CodeNode {id: $id})
                SET n.type = $type, n.name = $name, n.file = $file, n.line = $line
            """, **node)

    return {"indexed": len(nodes), "file": file_path}

@server.tool()
async def query_dependencies(symbol: str) -> dict:
    """
    Find all code that depends on or is depended by symbol.
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (n:CodeNode {name: $symbol})-[r:CALLS|IMPORTS|INHERITS*1..3]-(related)
            RETURN n, r, related
        """, symbol=symbol)

        return {
            "symbol": symbol,
            "dependencies": [dict(record) for record in result]
        }

@server.tool()
async def find_affected_by_change(file_path: str, function_name: str) -> dict:
    """
    Find all code affected if function is modified.
    """
    with driver.session() as session:
        result = session.run("""
            MATCH (changed:CodeNode {file: $file, name: $func})
            MATCH (affected:CodeNode)-[:CALLS*1..5]->(changed)
            RETURN DISTINCT affected.file AS file, affected.name AS name, affected.line AS line
            ORDER BY affected.file
        """, file=file_path, func=function_name)

        return {
            "changed": f"{file_path}:{function_name}",
            "affected": [dict(record) for record in result]
        }

@server.tool()
async def find_similar_code(description: str, top_k: int = 5) -> dict:
    """
    Find code similar to natural language description.

    Uses hybrid: keyword match + vector similarity (if embeddings stored).
    """
    with driver.session() as session:
        # Simple keyword search (enhance with embeddings in production)
        keywords = description.lower().split()
        result = session.run("""
            MATCH (n:CodeNode)
            WHERE ANY(kw IN $keywords WHERE toLower(n.name) CONTAINS kw)
            RETURN n.file AS file, n.name AS name, n.line AS line, n.type AS type
            LIMIT $k
        """, keywords=keywords, k=top_k)

        return {
            "query": description,
            "matches": [dict(record) for record in result]
        }

@server.tool()
async def get_call_graph(entry_point: str, depth: int = 3) -> dict:
    """
    Get call graph starting from entry point.
    """
    with driver.session() as session:
        result = session.run("""
            MATCH path = (start:CodeNode {name: $entry})-[:CALLS*1..$depth]->(called)
            RETURN path
        """, entry=entry_point, depth=depth)

        return {
            "entry": entry_point,
            "call_graph": [dict(record) for record in result]
        }

def extract_nodes(node, file_path, nodes=None):
    """Extract code nodes from AST (simplified)."""
    if nodes is None:
        nodes = []

    # Map tree-sitter node types to our types
    type_map = {
        "class_declaration": "class",
        "method_declaration": "function",
        "function_definition": "function",
        "function_item": "function",  # Rust
        "using_directive": "import",
    }

    if node.type in type_map:
        name_node = node.child_by_field_name("name")
        if name_node:
            nodes.append({
                "id": f"{file_path}:{node.start_point[0]}:{name_node.text.decode()}",
                "type": type_map[node.type],
                "name": name_node.text.decode(),
                "file": file_path,
                "line": node.start_point[0]
            })

    for child in node.children:
        extract_nodes(child, file_path, nodes)

    return nodes

if __name__ == "__main__":
    server.run()
```

---

## Quick Start

```bash
#!/bin/bash
# setup.sh - Complete setup script

set -e

echo "=== Claude Code Co-Agent Stack Setup ==="

# 1. Create directory structure
mkdir -p .claude/agents .claude/commands docs/decisions

# 2. Start infrastructure
docker-compose up -d
sleep 10  # Wait for services

# 3. Install MCPs
./install-mcps.sh

# 4. Copy agent definitions
# (copy from this document to .claude/agents/)

# 5. Copy command definitions
# (copy from this document to .claude/commands/)

# 6. Create CLAUDE.md
# (copy template and customize)

# 7. Verify
echo "Verifying services..."
curl -s http://localhost:8283/health && echo "✅ Letta OK"
curl -s http://localhost:6333/health && echo "✅ Qdrant OK"
curl -s http://localhost:7474 > /dev/null && echo "✅ Neo4j OK"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Usage:"
echo "  /scan              # Build knowledge base"
echo "  /plan \"task\"       # Research and design"
echo "  /implement         # TDD implementation"
echo "  /review            # Validate changes"
```

---

## Workflow Summary

### Unified Workflow (Auto-Detects Parallel)

```
┌─────────────────────────────────────────────────────────────────────┐
│  /scan                                                              │
│  Build knowledge: AST → Neo4j, Patterns → Letta                     │
│  MCPs: code-graph, letta                                            │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  /plan "your task"                                                  │
│                                                                     │
│  @researcher [think hard] → @architect [ultrathink]                │
│                    ↓                                                │
│  @orchestrator [think harder] analyzes for parallelization         │
│                    ↓                                                │
│  Output: Execution Mode = SEQUENTIAL or PARALLEL                   │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
                    ┌──────────────┴──────────────┐
                    ↓                             ↓
           Mode = SEQUENTIAL              Mode = PARALLEL
                    ↓                             ↓
┌───────────────────────────────┐ ┌───────────────────────────────────┐
│  /implement                   │ │  /implement                       │
│  Single @implementer          │ │  Spawns subagents per task        │
│  [think hard]                 │ │                                   │
│  TDD loop on all steps        │ │  ┌────────┐ ┌────────┐ ┌────────┐│
│                               │ │  │Agent A │ │Agent B │ │Agent C ││
│                               │ │  │Task A  │ │Task B  │ │Task C  ││
│                               │ │  └────────┘ └────────┘ └────────┘│
│                               │ │       ↓          ↓          ↓    │
│                               │ │            All complete          │
│                               │ │                  ↓                │
│                               │ │  /integrate (auto-triggered)     │
│                               │ │  Merge + validate consistency    │
└───────────────────────────────┘ └───────────────────────────────────┘
                    ↓                             ↓
                    └──────────────┬──────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  /review                                                            │
│  @reviewer [think hard]                                            │
│  Static Analysis → Security → Tests → Memory Check                  │
└─────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─────────────────────────────────────────────────────────────────────┐
│  @learner [think] (auto-triggered)                                 │
│  Extract patterns, store in memory                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### What the User Does

```
/scan                                    # Once, to build knowledge
/plan "Add auth and user management"    # System auto-detects mode
/implement                               # System uses detected mode
/review                                  # Final validation
```

That's it. **The system decides** if parallel execution is beneficial.

### When System Chooses Sequential

- Single subtask
- `--sequential` flag used
- Any file modified by 2+ subtasks
- Subtask A modifies dependency of B
- Estimated speedup < 30%

### When System Chooses Parallel

- Multiple subtasks with no conflicts
- All subtasks have exclusive file boundaries
- Clear isolation analysis passes
- Estimated speedup > 30%

### Override Flags

```
/plan --sequential "complex refactor"   # Force sequential
/implement --sequential                  # Force sequential even if plan allows parallel
/implement --task=A                      # Re-run specific parallel task
```

---

## MCP Summary Table

| MCP                     | Purpose                         | Used By                              |
| ----------------------- | ------------------------------- | ------------------------------------ |
| **filesystem**          | File operations                 | @implementer, subagents              |
| **git**                 | Version control                 | @implementer, @reviewer              |
| **github**              | PRs, issues                     | @reviewer                            |
| **sequential-thinking** | Complex reasoning               | @architect                           |
| **letta**               | Memory (74% accuracy)           | All agents                           |
| **code-graph**          | AST knowledge (75% improvement) | All agents, especially @orchestrator |
| **context7**            | Library docs                    | @researcher                          |
| **tavily**              | Web research                    | @researcher                          |
| **fetch**               | Direct URLs                     | @researcher                          |
| **semgrep**             | Security scanning               | @reviewer                            |
| **omnisharp**           | C# intelligence                 | @implementer, subagents              |
| **clangd**              | C/C++ intelligence              | @implementer, subagents              |
| **rust-analyzer**       | Rust intelligence               | @implementer, subagents              |
| **lua-language-server** | Lua intelligence                | @implementer, subagents              |
| **tot**                 | Tree-of-Thought (+70%)          | @architect                           |
| **reflection**          | Self-reflection (+21%)          | @implementer, @learner               |

---

## Agent Summary Table

| Agent             | Role                           | Thinking Level | Triggered By                   | MCPs                                 |
| ----------------- | ------------------------------ | -------------- | ------------------------------ | ------------------------------------ |
| **@researcher**   | Memory-first context gathering | `think hard`   | /plan                          | letta, code-graph, context7, tavily  |
| **@architect**    | ToT solution design            | `ultrathink`   | /plan                          | sequential-thinking, code-graph, tot |
| **@orchestrator** | Parallel execution analysis    | `think harder` | /plan (auto), /implement       | code-graph, letta                    |
| **@implementer**  | TDD coding                     | `think hard`   | /implement                     | filesystem, git, language servers    |
| **@reviewer**     | External validation            | `think hard`   | /review, /integrate            | semgrep, code-graph, letta           |
| **@learner**      | Pattern extraction             | `think`        | Auto after /implement, /review | letta, code-graph                    |

---

## Command Summary Table

| Command        | Purpose                                  | Agents                                 | Thinking               | Auto-Parallel       |
| -------------- | ---------------------------------------- | -------------------------------------- | ---------------------- | ------------------- |
| **/scan**      | Build knowledge graph                    | —                                      | —                      | No                  |
| **/plan**      | Research + design + auto-detect parallel | @researcher, @architect, @orchestrator | ultrathink (architect) | Auto-detects        |
| **/implement** | TDD implementation (auto-selects mode)   | @implementer, @orchestrator            | think hard             | Uses /plan mode     |
| **/integrate** | Merge + validate parallel work           | @reviewer                              | think hard             | Auto after parallel |
| **/review**    | Final validation                         | @reviewer                              | think hard             | No                  |

### Simplified User Commands

You only need **4 commands**:

```
/scan                  # Build knowledge (once per project)
/plan "task"           # Research, design, auto-detect mode
/implement             # Execute (sequential or parallel based on plan)
/review                # Validate
```

The system handles everything else automatically.
