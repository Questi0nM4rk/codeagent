# CodeAgent: Research-Backed Autonomous Coding Framework

> Zero assumptions. 100% accuracy. Memory-first intelligence.

---

## Vision

**Build an autonomous coding system that never guesses.**

Current AI coding assistants fail because they:

- Hallucinate APIs and patterns that don't exist
- Forget context from previous sessions
- Self-validate their own mistakes
- Fragment context across multiple agents

CodeAgent solves this by implementing research-backed patterns from 1,400+ academic papers, prioritizing **accuracy over speed** and **memory over assumptions**.

---

## Core Philosophy

### 0. Partner, Not Assistant

**CodeAgent is a thinking partner, not a compliant tool.**

The system is designed to work alongside developers as a senior colleague who:
- **Challenges assumptions** - Questions the first idea, proposes alternatives
- **Says "I don't know"** - Admits uncertainty rather than guessing
- **Pushes back on bad ideas** - Respectfully disagrees when something smells wrong
- **Treats every interaction as brainstorming** - Presents options, surfaces tradeoffs, invites discussion

This is not about being difficult. It's about producing better outcomes through rigorous thinking and evidence-based decisions.

### 1. Memory-First Intelligence

```
Query Order: Project Memory → Code Graph → External Docs → Web Search
                   ↓
         "I don't know" if nothing found
```

The system checks what it already knows before reaching for external sources. If it doesn't know something with certainty, it says so - **never fabricates answers**.

### 2. Smart Parallelization

```
Research says: "Multi-agent fragments context"
Reality: That's for SHARED code

Parallel works when tasks are ISOLATED:
  Agent A: UserController (own files)
  Agent B: ProductController (own files)
  → No shared code = no fragmentation
  → Just parallel speed

Sequential when tasks SHARE code:
  Agent A: UserController (uses JwtService)
  Agent B: AuthController (modifies JwtService)
  → Shared dependency = use single agent
```

### 3. External Validation Only

LLMs asked to verify their own code miss 60-80% of errors. CodeAgent uses:

- Static analysis (linters, type checkers)
- Security scanning (Semgrep)
- Test execution (real pass/fail)
- Memory consistency checks

Never self-validation.

### 4. Test-Driven Development

```
Write Test → Run (must fail) → Commit Test → Write Code → Run (must pass) → Commit Code
```

No implementation without tests. No test modification to pass. Maximum 3 attempts before escalation.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER                                        │
│         /scan  /plan  /plan-parallel  /implement  /integrate  /review   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMMAND LAYER                                    │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ /scan   │ │ /plan   │ │/plan-parallel │ │ /implement  │ │ /review │ │
│  │ Build   │ │ Design  │ │ Isolation     │ │ TDD Loop    │ │Validate │ │
│  │Knowledge│ │ Solo    │ │ Analysis      │ │ or Parallel │ │External │ │
│  └─────────┘ └─────────┘ └───────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                     │
│ ┌──────────┐┌───────────┐┌────────────┐┌─────────────┐┌────────┐┌─────┐│
│ │Researcher││ Architect ││Orchestrator││ Implementer ││Reviewer││Learn││
│ │ Context  ││ Design    ││ Parallel   ││ TDD Code    ││Validate││Ptrns││
│ │ Gather   ││ ToT       ││ Analysis   ││ Patterns    ││External││     ││
│ └──────────┘└───────────┘└────────────┘└─────────────┘└────────┘└─────┘│
│                               │                                         │
│                    ┌──────────┴──────────┐                              │
│                    ▼                     ▼                              │
│              ┌──────────┐          ┌──────────┐    (Parallel mode)     │
│              │Subagent A│          │Subagent B│                        │
│              │Isolated  │          │Isolated  │                        │
│              └──────────┘          └──────────┘                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           MCP LAYER                                      │
│                                                                          │
│  CORE           MEMORY          RESEARCH        LANGUAGE     VALIDATION │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  ┌─────────┐│
│  │filesystem│   │ letta    │   │ context7 │   │omnisharp │  │ semgrep ││
│  │ git      │   │code-graph│   │ tavily   │   │ clangd   │  │ linters ││
│  │ github   │   │ memory   │   │ fetch    │   │rust-anlzr│  │ tests   ││
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘  └─────────┘│
│                                                                          │
│  CUSTOM (Research-Backed)                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                     │
│  │ ToT MCP      │ │ Reflection   │ │ Code-Graph   │                     │
│  │ +70% complex │ │ +21% coding  │ │ +75% retrieval│                    │
│  └──────────────┘ └──────────────┘ └──────────────┘                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       INFRASTRUCTURE LAYER                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │    Neo4j     │ │    Qdrant    │ │    Letta     │ │   Ollama     │   │
│  │  Code Graph  │ │ Vector Store │ │   Memory     │ │  Embeddings  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Research Foundation

This framework implements findings from:

| Source                                                          | Key Finding                     | Implementation                      |
| --------------------------------------------------------------- | ------------------------------- | ----------------------------------- |
| **Context Engineering Survey** (arXiv:2507.13334, 1400+ papers) | Context assembly C = A(c₁...cₙ) | Memory-first retrieval hierarchy    |
| **Cognition Labs** (Devin creators)                             | Multi-agent fragments context   | Single-agent implementation         |
| **SWE-bench**                                                   | Single agents achieve 70%+      | @implementer as sole coder          |
| **Tree-of-Thought** (ToT)                                       | +70% on complex reasoning       | ToT MCP for @architect              |
| **Reflexion** (NeurIPS 2023)                                    | +21% on HumanEval               | Reflection MCP with episodic memory |
| **GraphRAG research**                                           | +75% code retrieval             | Neo4j code-graph MCP                |
| **Letta benchmarks**                                            | 74% LOCOMO accuracy             | Letta as primary memory             |
| **Static analysis studies**                                     | 70-75% more errors caught       | External validation pipeline        |

---

## Target Users

- **Senior developers** building production systems
- **Not beginners** — no hand-holding, no fluff
- **Accuracy-focused** — willing to spend tokens for correctness
- **Multi-language** — .NET, C/C++, Rust, Lua, Bash

---

## Language Support

| Language     | LSP                 | Linter                   | Test Runner   |
| ------------ | ------------------- | ------------------------ | ------------- |
| C# (.NET 10) | OmniSharp           | `dotnet format`          | `dotnet test` |
| C++ (C++23)  | clangd              | `clang-tidy`, `cppcheck` | `ctest`       |
| C            | clangd              | `clang-tidy`, `cppcheck` | `ctest`       |
| Rust         | rust-analyzer       | `cargo clippy`           | `cargo test`  |
| Lua          | lua-language-server | `luacheck`               | `busted`      |
| Bash/Zsh     | —                   | `shellcheck`             | `bats`        |

---

## Workflow

### Unified Flow (System Auto-Detects Parallel)

```
┌─────────────────────────────────────────────────────────────────┐
│  /scan                                                          │
│  Parse codebase → Build AST graph → Extract patterns → Store   │
│  Output: X% completeness, knowledge gaps identified             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  /plan "task description"                                       │
│                                                                 │
│  @researcher [think hard]: Memory → Code-graph → Context7      │
│  @architect [ultrathink]: Decompose → Generate 3+ approaches   │
│  @orchestrator [think harder]: Analyze isolation boundaries    │
│                                                                 │
│  Output:                                                        │
│  - Design document                                              │
│  - Execution Mode: SEQUENTIAL or PARALLEL (auto-detected)      │
│  - If PARALLEL: File boundaries per task                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  /implement                                                     │
│                                                                 │
│  If SEQUENTIAL:                If PARALLEL:                    │
│  Single @implementer           Spawn subagents per task        │
│  TDD loop on all steps         ┌────────┐ ┌────────┐           │
│                                │Agent A │ │Agent B │           │
│                                └────────┘ └────────┘           │
│                                     ↓                          │
│                                /integrate (auto)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  /review                                                        │
│  @reviewer [think hard]: Lint → Security → Tests → Memory      │
│  External tools only, never self-validation                     │
│  Output: APPROVED or CHANGES REQUIRED with specific fixes       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  @learner [think] (auto-triggered)                              │
│  Extract patterns → Store in Letta → Update code-graph         │
│  System gets smarter with every task                            │
└─────────────────────────────────────────────────────────────────┘
```

### What You Type

```bash
/scan                           # Once per project
/plan "add auth and profiles"   # System decides: SEQUENTIAL or PARALLEL
/implement                      # Executes in detected mode
/review                         # Final validation
```

That's it. **4 commands. The system handles the rest.**

---

## Key Differentiators vs SuperClaude

| Feature            | SuperClaude          | CodeAgent                               |
| ------------------ | -------------------- | --------------------------------------- |
| **Agents**         | 16 general-purpose   | 5 specialized for accuracy              |
| **Memory**         | Basic persistence    | Letta (74%) + Neo4j code graph          |
| **Implementation** | Multi-agent possible | Single-agent enforced (research-backed) |
| **Validation**     | Self-review          | External tools only                     |
| **Reasoning**      | Sequential thinking  | ToT (+70%) + Reflection (+21%)          |
| **Focus**          | Broad productivity   | Accuracy-optimized coding               |
| **Custom MCPs**    | None                 | 3 research-backed tools                 |

---

## Success Metrics

| Metric                   | Target                     | How                          |
| ------------------------ | -------------------------- | ---------------------------- |
| **SWE-bench resolution** | 70%+                       | Single-agent TDD loop        |
| **Memory accuracy**      | 74%+                       | Letta + episodic reflection  |
| **Code retrieval**       | 75%+ improvement           | Neo4j graph + vector hybrid  |
| **Error detection**      | 70%+ more than self-review | External validation pipeline |
| **Context retention**    | 100% across sessions       | Letta + CLAUDE.md hierarchy  |

---

## Non-Goals

- **Speed optimization** — we trade tokens for accuracy
- **Beginner tutorials** — target audience is senior devs
- **GUI/IDE integration** — CLI-first (Claude Code)
- **All languages** — focused stack (.NET, C/C++, Rust, Lua)
- **Cloud deployment** — local-first, self-hosted

---

## Roadmap

### Phase 1: Foundation (Current)

- [x] Architecture design
- [x] Agent definitions
- [x] Command structure
- [x] MCP stack selection
- [ ] Infrastructure setup (Docker)
- [ ] Base installation script

### Phase 2: Core MCPs

- [ ] Code-Graph MCP (Neo4j + Tree-sitter)
- [ ] ToT MCP (Tree-of-Thought reasoning)
- [ ] Reflection MCP (episodic memory)

### Phase 3: Polish

- [ ] Language-specific optimizations
- [ ] Hook configurations
- [ ] Documentation
- [ ] Example projects

### Phase 4: Release

- [ ] GitHub repo
- [ ] One-line installer
- [ ] Community feedback

---

## Installation (Target)

```bash
# One-line install (like SuperClaude)
curl -fsSL https://raw.githubusercontent.com/USER/codeagent/main/install.sh | bash

# Or manual
git clone https://github.com/USER/codeagent.git ~/.codeagent
cd ~/.codeagent && ./install.sh

# Start infrastructure
codeagent start

# Use in any project
cd /your/project
codeagent init  # Creates CLAUDE.md, .claude/
```

---

## Philosophy Summary

> "It's better to say 'I don't know' than to guess and be wrong."
> "It's better to push back on a bad idea now than to revert it later."
> "You are a partner, not just a tool."

### The Partner Mindset

| Traditional Assistant | CodeAgent Partner |
|----------------------|-------------------|
| "Sure, I'll implement that" | "Before I implement - have you considered X?" |
| "Here's the solution" | "Here are 3 approaches with tradeoffs" |
| Guesses when uncertain | "I'm not confident about this - let me explain why" |
| Accepts all requests | "I'd push back on that because..." |
| Provides answers | Starts conversations |

### Core Principles

1. **Partner before tool** — challenge, discuss, collaborate
2. **Uncertainty before confidence** — say "I don't know" when unsure
3. **Memory before search** — use what you know
4. **Graph before vector** — understand structure
5. **External before self** — validate independently
6. **Test before code** — TDD always
7. **Single before multi** — coherent context
8. **Accuracy before speed** — correctness matters

### Skill Personalities

Each skill embodies the partner mindset differently:

| Skill | Partner Behavior |
|-------|------------------|
| **researcher** | "I found X, but I'm uncertain about Y - here are the gaps" |
| **architect** | "Your approach could work, but let me show you 2 alternatives" |
| **orchestrator** | "I can't verify this is safe to parallelize - recommend sequential" |
| **implementer** | "I'm stuck after 3 attempts - let's step back and reconsider" |
| **reviewer** | "I found issues - these need to be fixed before approval" |
| **learner** | "Nothing new to extract here - this followed existing patterns" |

---

## License

MIT — Use it, fork it, improve it.
