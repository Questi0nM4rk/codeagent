# Claude Code Configuration Workflow

> Comprehensive design document for installing, configuring, and managing Claude Code configurations in CodeAgent.
> This document uses **Skills** as the reference implementation. Commands, hooks, and settings follow the same pattern.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration Categories](#configuration-categories)
4. [Skills Reference Implementation](#skills-reference-implementation)
5. [Installation Workflow](#installation-workflow)
6. [Script Design](#script-design)
7. [Configuration File Formats](#configuration-file-formats)
8. [Validation System](#validation-system)
9. [Update and Force Reinstall](#update-and-force-reinstall)
10. [Error Handling](#error-handling)
11. [Testing Strategy](#testing-strategy)

---

## Overview

### Problem Statement

Claude Code configurations (skills, commands, hooks, settings) require a consistent, repeatable installation process that:
- Works on fresh systems (first install)
- Updates existing installations (re-run without --force)
- Completely rebuilds from scratch (re-run with --force)
- Handles user-level (~/.claude/) and project-level (.claude/) configurations
- Respects existing user configurations (backup/merge options)
- Validates everything works before declaring success

### Goals

1. **Idempotent** - Running twice produces the same result
2. **Non-destructive by default** - Preserve user's existing configs unless --force
3. **Backup-first** - Always backup before modifying existing files
4. **Validatable** - Check that installed configs are syntactically correct
5. **Extensible** - Easy to add new skills/commands following the same pattern

### Non-Goals

- Modifying project-level configs (those are per-project via `codeagent init`)
- Managing enterprise/managed configurations
- GUI configuration editor

---

## Architecture

### Directory Structure

```
Source (CodeAgent repo):
~/Projects/claude-project/
├── framework/
│   ├── skills/                   # Skill definitions
│   │   ├── researcher/
│   │   │   └── SKILL.md
│   │   ├── architect/
│   │   │   └── SKILL.md
│   │   ├── orchestrator/
│   │   │   └── SKILL.md
│   │   ├── implementer/
│   │   │   └── SKILL.md
│   │   ├── reviewer/
│   │   │   └── SKILL.md
│   │   └── learner/
│   │       └── SKILL.md
│   ├── commands/                 # Slash command definitions
│   │   ├── scan.md
│   │   ├── plan.md
│   │   ├── implement.md
│   │   ├── integrate.md
│   │   └── review.md
│   ├── hooks/                    # Hook scripts
│   │   ├── pre-commit.sh
│   │   ├── post-implement.sh
│   │   └── index-file.sh
│   └── settings.json.template    # Settings template
└── templates/
    └── CLAUDE.md.template        # Global CLAUDE.md template

Target (User's system):
~/.claude/
├── CLAUDE.md                     # Global memory/instructions
├── settings.json                 # Global settings
├── skills/                       # User-level skills
│   ├── researcher/
│   │   └── SKILL.md
│   ├── architect/
│   │   └── SKILL.md
│   └── ...
├── commands/                     # User-level commands
│   ├── scan.md
│   ├── plan.md
│   └── ...
└── hooks/                        # User-level hooks
    ├── pre-commit.sh
    └── ...
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
│                  install-claude-config.sh                        │
│  (orchestrates Claude Code config installation)                  │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│    Skills     │      │   Commands    │      │    Hooks      │
│ (researcher,  │      │ (scan, plan,  │      │ (pre-commit,  │
│  architect,   │      │  implement,   │      │  post-impl,   │
│  etc.)        │      │  etc.)        │      │  etc.)        │
└───────────────┘      └───────────────┘      └───────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              ~/.claude/ (User Configuration)                     │
│  skills/, commands/, hooks/, settings.json, CLAUDE.md           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration Categories

Claude Code configurations fall into five categories:

### Category 1: Skills

Autonomous capabilities Claude discovers and activates based on context.

**Structure:**
```
~/.claude/skills/skill-name/
└── SKILL.md                      # Required - skill definition
```

**Key Characteristics:**
- Model-invoked (Claude decides when to use)
- Multi-file directories with SKILL.md entry point
- Activated based on description matching user request
- Can reference supporting files

**CodeAgent Skills:**
- `researcher` - Memory-first context gathering
- `architect` - Tree-of-Thought solution design
- `orchestrator` - Parallel execution analysis
- `implementer` - Strict TDD workflow
- `reviewer` - External validation
- `learner` - Pattern extraction

### Category 2: Commands

Explicit prompts invoked with `/command-name` syntax.

**Structure:**
```
~/.claude/commands/
└── command-name.md               # Single file per command
```

**Key Characteristics:**
- User-invoked (explicit /command)
- Single markdown file per command
- Can accept arguments ($1, $2, $ARGUMENTS)
- Can execute bash commands with allowed-tools

**CodeAgent Commands:**
- `/scan` - Build knowledge graph
- `/plan` - Research & design
- `/implement` - TDD execution
- `/integrate` - Merge parallel work
- `/review` - External validation

### Category 3: Hooks

Scripts that execute in response to Claude Code events.

**Structure:**
```
~/.claude/hooks/
└── script-name.sh                # Executable script
```

**Key Characteristics:**
- Event-driven (PreToolUse, PostToolUse, etc.)
- Must be executable (chmod +x)
- Exit code determines behavior (0=success, 2=block)
- Receives JSON input via stdin

**CodeAgent Hooks:**
- `pre-commit.sh` - Validate before git commit
- `post-implement.sh` - Run tests after implementation
- `index-file.sh` - Update knowledge graph after file changes

### Category 4: Settings

Global configuration in JSON format.

**Structure:**
```
~/.claude/settings.json           # Single JSON file
```

**Key Characteristics:**
- Permissions (allow/deny/ask rules)
- Hooks configuration
- Environment variables
- MCP server controls
- Model preferences

### Category 5: Memory (CLAUDE.md)

Persistent instructions and context.

**Structure:**
```
~/.claude/CLAUDE.md               # Markdown instructions
~/.claude/rules/                  # Optional modular rules
└── topic.md
```

**Key Characteristics:**
- Plain English instructions
- Project context and conventions
- Development commands
- Loaded automatically in every session

---

## Skills Reference Implementation

Skills are the most complex configuration because they:
1. Have a specific directory structure (skill-name/SKILL.md)
2. Require valid YAML frontmatter
3. Must have discoverable descriptions
4. Can have optional supporting files

### Skill File Format

```markdown
---
name: skill-name
description: Brief description of what this skill does and WHEN to use it. Include trigger keywords.
allowed-tools: Read, Grep, Glob  # Optional - restricts available tools
---

# Skill Name

## Identity
[Who is Claude when this skill is active]

## Personality
[How Claude should behave - partner, not assistant]

## Process
[Step-by-step workflow]

## Output Format
[Expected output structure]

## Rules
[Strict rules to follow]
```

### Skill Anatomy: Researcher Example

```yaml
---
name: researcher
description: Research specialist for gathering context before implementation. Activates when researching codebases, understanding existing patterns, or gathering information before making changes. Uses memory-first approach.
---
```

**Discovery Triggers (from description):**
- "researching codebases"
- "understanding existing patterns"
- "gathering information"
- "before making changes"
- "memory-first"

**Key Sections:**
1. **Identity** - Defines who Claude is (senior technical researcher)
2. **Personality** - Partner behavior (honest about uncertainty, push back, brainstorm)
3. **Research Priority** - Strict order: Memory → Codebase → External
4. **Extended Thinking** - When to use `think hard`
5. **Output Format** - Structured markdown template
6. **Rules** - Non-negotiable constraints

### Skill Validation Requirements

| Check | Requirement | Error Message |
|-------|-------------|---------------|
| Directory exists | `skill-name/` is a directory | "Skill must be a directory" |
| SKILL.md exists | `SKILL.md` file present | "Missing SKILL.md" |
| Valid YAML | Frontmatter parses correctly | "Invalid YAML frontmatter" |
| Name field | `name` in frontmatter | "Missing required field: name" |
| Description field | `description` in frontmatter | "Missing required field: description" |
| Name matches directory | `name` == directory name | "Name mismatch: X vs Y" |
| Description length | < 1024 characters | "Description too long" |

---

## Installation Workflow

### Phase 1: Pre-flight Checks

Before installing any configuration:

```
1. Check Claude Code CLI installed
   └─ command -v claude

2. Check existing state
   ├─ Does ~/.claude/ exist?
   ├─ Does ~/.claude/settings.json exist?
   ├─ Does ~/.claude/CLAUDE.md exist?
   ├─ How many existing skills/commands/hooks?
   └─ Any custom modifications?

3. Determine installation mode
   ├─ --force flag? → Full reinstall (backup and replace everything)
   ├─ No flag, exists? → Update (only change CodeAgent-managed configs)
   └─ No flag, fresh? → Fresh install
```

### Phase 2: Backup (if updating existing)

```
1. Create timestamped backup directory
   └─ ~/.claude-backup-YYYYMMDD_HHMMSS/

2. Copy existing configs to backup
   ├─ settings.json
   ├─ CLAUDE.md
   ├─ skills/
   ├─ commands/
   └─ hooks/

3. Record backup location for user
```

### Phase 3: User Choice (interactive)

If existing configs detected and not --force:

```
Existing Claude Code configuration detected:
  - ~/.claude/CLAUDE.md
  - ~/.claude/settings.json
  - ~/.claude/skills/ (3 skills)
  - ~/.claude/commands/ (5 commands)

Options:
  1) Backup existing and install CodeAgent config (recommended)
  2) Merge (keep existing, add CodeAgent additions)
  3) Skip (don't modify existing config)

Choose option [1/2/3]:
```

### Phase 4: Install Skills

For each skill in source framework/skills/:

```
1. Create skill directory
   └─ mkdir -p ~/.claude/skills/$skill_name/

2. Copy SKILL.md
   └─ cp framework/skills/$skill_name/SKILL.md ~/.claude/skills/$skill_name/

3. Copy supporting files (if any)
   └─ cp framework/skills/$skill_name/* ~/.claude/skills/$skill_name/

4. Validate skill
   └─ Check YAML frontmatter is valid
   └─ Check name matches directory
```

### Phase 5: Install Commands

For each command in source framework/commands/:

```
1. Create commands directory
   └─ mkdir -p ~/.claude/commands/

2. Copy command file
   └─ cp framework/commands/$command.md ~/.claude/commands/

3. Validate command
   └─ Check YAML frontmatter is valid
   └─ Check description field exists
```

### Phase 6: Install Hooks

For each hook in source framework/hooks/:

```
1. Create hooks directory
   └─ mkdir -p ~/.claude/hooks/

2. Copy hook script
   └─ cp framework/hooks/$hook.sh ~/.claude/hooks/

3. Make executable
   └─ chmod +x ~/.claude/hooks/$hook.sh

4. Validate hook
   └─ Check script is valid bash (bash -n)
```

### Phase 7: Install Settings

```
1. If fresh install or --force:
   └─ Copy settings.json.template → ~/.claude/settings.json

2. If merge mode:
   └─ Parse existing settings.json
   └─ Add CodeAgent permissions to existing allow list
   └─ Preserve user's custom settings
   └─ Write merged settings.json

3. Validate settings
   └─ Check JSON is valid (jq .)
```

### Phase 8: Install CLAUDE.md

```
1. If fresh install or --force:
   └─ Copy CLAUDE.md.template → ~/.claude/CLAUDE.md

2. If merge mode:
   └─ Append CodeAgent section to existing CLAUDE.md
   └─ Only if "CodeAgent Integration" section not already present

3. Validate CLAUDE.md
   └─ Check file exists and is readable
```

### Phase 9: Verification

After all configs installed:

```
1. Count installed components
   ├─ Skills: ls ~/.claude/skills/ | wc -l
   ├─ Commands: ls ~/.claude/commands/*.md | wc -l
   └─ Hooks: ls ~/.claude/hooks/*.sh | wc -l

2. Validate each component
   └─ Run validation checks from Phase 4-6

3. Report summary
   ├─ Installed: X skills, Y commands, Z hooks
   ├─ Any validation errors
   └─ Backup location (if applicable)
```

---

## Script Design

### Main Entry Point: install.sh

```bash
#!/bin/bash
# install.sh - Main CodeAgent installer

# Parse args
FORCE=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --force|-f) FORCE=true; shift ;;
    *) shift ;;
  esac
done

# Export for sub-scripts
export CODEAGENT_FORCE=$FORCE

# ... other setup (requirements, MCPs, etc.) ...

# Call Claude config installer
"$INSTALL_DIR/scripts/install-claude-config.sh"
```

### Claude Config Installer: install-claude-config.sh

The config installer should:

1. Check existing state
2. Handle backup/merge/skip choice
3. Install each category
4. Validate all installations
5. Report results

**Pseudocode structure:**

```bash
#!/bin/bash
# install-claude-config.sh

FORCE=${CODEAGENT_FORCE:-false}
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
CLAUDE_DIR="$HOME/.claude"
SOURCE_DIR="$INSTALL_DIR/framework"

# Phase 1: Pre-flight
check_claude_cli
check_existing_state

# Phase 2-3: Handle existing configs
if has_existing_configs; then
  if [ "$FORCE" = true ]; then
    backup_and_clean
  else
    prompt_user_choice  # Returns: replace, merge, skip
  fi
fi

# Phase 4-6: Install components
install_skills
install_commands
install_hooks

# Phase 7-8: Install settings and memory
install_settings
install_claude_md

# Phase 9: Verify
verify_all_configs
report_summary
```

### Config Registry: config-registry.json

Central configuration for all Claude Code configs:

```json
{
  "version": "1.0",
  "skills": [
    {
      "name": "researcher",
      "description": "Memory-first context gathering",
      "source": "framework/skills/researcher",
      "files": ["SKILL.md"]
    },
    {
      "name": "architect",
      "description": "Tree-of-Thought solution design",
      "source": "framework/skills/architect",
      "files": ["SKILL.md"]
    },
    {
      "name": "orchestrator",
      "description": "Parallel execution analysis",
      "source": "framework/skills/orchestrator",
      "files": ["SKILL.md"]
    },
    {
      "name": "implementer",
      "description": "Strict TDD workflow",
      "source": "framework/skills/implementer",
      "files": ["SKILL.md"]
    },
    {
      "name": "reviewer",
      "description": "External validation",
      "source": "framework/skills/reviewer",
      "files": ["SKILL.md"]
    },
    {
      "name": "learner",
      "description": "Pattern extraction",
      "source": "framework/skills/learner",
      "files": ["SKILL.md"]
    }
  ],
  "commands": [
    {
      "name": "scan",
      "description": "Build knowledge graph",
      "source": "framework/commands/scan.md"
    },
    {
      "name": "plan",
      "description": "Research & design",
      "source": "framework/commands/plan.md"
    },
    {
      "name": "implement",
      "description": "TDD execution",
      "source": "framework/commands/implement.md"
    },
    {
      "name": "integrate",
      "description": "Merge parallel work",
      "source": "framework/commands/integrate.md"
    },
    {
      "name": "review",
      "description": "External validation",
      "source": "framework/commands/review.md"
    }
  ],
  "hooks": [
    {
      "name": "pre-commit",
      "description": "Validate before git commit",
      "source": "framework/hooks/pre-commit.sh",
      "event": "PreToolUse",
      "matcher": "Bash(git commit:*)"
    },
    {
      "name": "post-implement",
      "description": "Run tests after implementation",
      "source": "framework/hooks/post-implement.sh",
      "event": "PostToolUse",
      "matcher": "Write|Edit"
    },
    {
      "name": "index-file",
      "description": "Update knowledge graph",
      "source": "framework/hooks/index-file.sh",
      "event": "PostToolUse",
      "matcher": "Write"
    }
  ],
  "settings": {
    "source": "framework/settings.json.template",
    "merge_strategy": "append_permissions"
  },
  "memory": {
    "source": "templates/CLAUDE.md.template",
    "merge_strategy": "append_section"
  }
}
```

---

## Configuration File Formats

### Skills: SKILL.md

```yaml
---
name: skill-name                  # Required: lowercase, hyphens, max 64 chars
description: What and WHEN        # Required: max 1024 chars, discovery triggers
allowed-tools: Tool1, Tool2       # Optional: restrict tools when active
---

# Skill Title

[Markdown content with instructions for Claude]
```

### Commands: command.md

```yaml
---
description: One-liner for /help  # Required: shown in autocomplete
allowed-tools: Bash(git:*)        # Optional: restrict tool access
argument-hint: [arg1] [arg2]      # Optional: usage hint
model: claude-sonnet-4-5-20250929 # Optional: specific model
---

# Command Instructions

[Markdown prompt content]

Use $ARGUMENTS for all args, or $1, $2, etc. for positional.
Use !`command` for bash output (must declare in allowed-tools).
Use @path/to/file for file references.
```

### Hooks: script.sh

```bash
#!/bin/bash
# Hook script

# Read JSON input from stdin
input=$(cat)

# Parse relevant fields
tool_name=$(echo "$input" | jq -r '.tool_name')
tool_input=$(echo "$input" | jq -r '.tool_input')

# Do validation/processing

# Exit codes:
# 0 = success (stdout shown in verbose mode)
# 2 = block (stderr used as error message)
# other = non-blocking error
```

### Settings: settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(npm:*)",
      "Bash(git:*)",
      "Read(**/*)",
      "Edit(**/*)",
      "mcp__*"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Read(.env)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/hooks/post-implement.sh"
          }
        ]
      }
    ]
  },
  "env": {
    "CODEAGENT_HOME": "$HOME/.codeagent"
  }
}
```

### Memory: CLAUDE.md

```markdown
# Global Claude Configuration

## Identity
[Who Claude is in this context]

## Principles
[Guiding principles for behavior]

## Languages
[Supported programming languages]

## Response Style
[How to format responses]

## CodeAgent Integration
This configuration is managed by CodeAgent.
Run `codeagent init` in your project for project-specific setup.
```

---

## Validation System

### Skill Validation

```bash
validate_skill() {
  local skill_dir=$1
  local skill_name=$(basename "$skill_dir")

  # Check directory exists
  [ -d "$skill_dir" ] || return 1

  # Check SKILL.md exists
  [ -f "$skill_dir/SKILL.md" ] || return 1

  # Extract frontmatter
  local frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_dir/SKILL.md" | sed '1d;$d')

  # Check YAML is valid
  echo "$frontmatter" | yq . > /dev/null 2>&1 || return 1

  # Check required fields
  local name=$(echo "$frontmatter" | yq -r '.name')
  local desc=$(echo "$frontmatter" | yq -r '.description')

  [ -n "$name" ] && [ "$name" != "null" ] || return 1
  [ -n "$desc" ] && [ "$desc" != "null" ] || return 1

  # Check name matches directory
  [ "$name" = "$skill_name" ] || return 1

  # Check description length
  [ ${#desc} -lt 1024 ] || return 1

  return 0
}
```

### Command Validation

```bash
validate_command() {
  local cmd_file=$1

  # Check file exists
  [ -f "$cmd_file" ] || return 1

  # Extract frontmatter
  local frontmatter=$(sed -n '/^---$/,/^---$/p' "$cmd_file" | sed '1d;$d')

  # Check YAML is valid
  echo "$frontmatter" | yq . > /dev/null 2>&1 || return 1

  # Check description exists
  local desc=$(echo "$frontmatter" | yq -r '.description')
  [ -n "$desc" ] && [ "$desc" != "null" ] || return 1

  return 0
}
```

### Hook Validation

```bash
validate_hook() {
  local hook_file=$1

  # Check file exists
  [ -f "$hook_file" ] || return 1

  # Check is executable
  [ -x "$hook_file" ] || return 1

  # Check bash syntax
  bash -n "$hook_file" 2>/dev/null || return 1

  return 0
}
```

### Settings Validation

```bash
validate_settings() {
  local settings_file=$1

  # Check file exists
  [ -f "$settings_file" ] || return 1

  # Check JSON is valid
  jq . "$settings_file" > /dev/null 2>&1 || return 1

  # Check required structure
  jq -e '.permissions' "$settings_file" > /dev/null 2>&1 || return 1

  return 0
}
```

---

## Update and Force Reinstall

### Normal Update (no flags)

```
1. Check what's already installed
   ├─ List existing skills
   ├─ List existing commands
   └─ List existing hooks

2. For skills:
   ├─ If skill exists and matches → skip
   ├─ If skill exists and differs → prompt to update
   └─ If skill missing → install

3. For commands:
   ├─ If command exists and matches → skip
   ├─ If command exists and differs → prompt to update
   └─ If command missing → install

4. For hooks:
   ├─ If hook exists and matches → skip
   ├─ If hook exists and differs → prompt to update
   └─ If hook missing → install

5. For settings:
   └─ Merge CodeAgent permissions with existing

6. For CLAUDE.md:
   └─ Append CodeAgent section if not present
```

### Force Reinstall (--force flag)

```
1. Create backup of existing ~/.claude/
   └─ ~/.claude-backup-YYYYMMDD_HHMMSS/

2. Remove CodeAgent-managed components
   ├─ rm -rf ~/.claude/skills/researcher/
   ├─ rm -rf ~/.claude/skills/architect/
   ├─ ... (all CodeAgent skills)
   ├─ rm ~/.claude/commands/scan.md
   ├─ rm ~/.claude/commands/plan.md
   ├─ ... (all CodeAgent commands)
   └─ rm ~/.claude/hooks/*.sh

3. Fresh install all components
   ├─ Copy all skills
   ├─ Copy all commands
   ├─ Copy all hooks
   ├─ Replace settings.json
   └─ Replace CLAUDE.md

4. Verify all from scratch
```

### Preserving User Customizations

Even with --force:
- User's custom skills (not in config-registry) are preserved
- User's custom commands are preserved
- User's custom hooks are preserved
- Backup is always created first
- User is warned about what will be replaced

---

## Error Handling

### Error Categories

| Category | Example | Recovery |
|----------|---------|----------|
| Missing Claude CLI | `claude` not found | Exit with install instructions |
| Permission Error | Can't write to ~/.claude/ | Suggest permissions fix |
| Invalid YAML | Malformed frontmatter | Show parsing error, skip file |
| Missing Required Field | No description in command | Show error, skip file |
| Disk Full | Can't copy files | Exit with clear message |
| Backup Failed | Can't create backup | Exit before making changes |

### Error Messages

Every error should include:
1. What failed
2. Why it might have failed
3. How to fix it

**Example:**
```
[ERROR] Failed to validate skill: architect

Problem: Invalid YAML frontmatter in SKILL.md

Details:
  File: ~/.claude/skills/architect/SKILL.md
  Line 3: unexpected end of stream

To fix:
  1. Check YAML syntax (proper indentation, no tabs)
  2. Ensure frontmatter is between --- markers
  3. Validate with: yq . ~/.claude/skills/architect/SKILL.md

Skipping this skill. Other installations will continue.
```

### Rollback Strategy

If installation fails partway:
1. Log what was completed
2. Don't undo completed steps (idempotent design)
3. User can re-run to continue from where it failed
4. --force flag available for clean slate
5. Backup available for manual restoration

---

## Testing Strategy

### Unit Tests

For each validation function:
- `validate_skill` - test with valid/invalid skills
- `validate_command` - test with valid/invalid commands
- `validate_hook` - test with valid/invalid scripts
- `validate_settings` - test with valid/invalid JSON

### Integration Tests

1. **Fresh Install Test**
   ```bash
   # Clean slate
   rm -rf ~/.claude/

   # Install
   ./install.sh

   # Verify
   ls ~/.claude/skills/
   ls ~/.claude/commands/
   ls ~/.claude/hooks/
   cat ~/.claude/settings.json | jq .
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
   # Install, modify a skill, force reinstall
   ./install.sh
   echo "# Modified" >> ~/.claude/skills/researcher/SKILL.md
   ./install.sh --force

   # Verify skill is restored to original
   # Verify backup was created
   ```

4. **Merge Test**
   ```bash
   # Create custom skill
   mkdir -p ~/.claude/skills/my-custom/
   echo "---\nname: my-custom\ndescription: test\n---\n# Test" > ~/.claude/skills/my-custom/SKILL.md

   # Run install with merge
   ./install.sh  # Choose option 2 (merge)

   # Verify custom skill preserved
   ls ~/.claude/skills/my-custom/
   ```

### Smoke Tests

Quick verification that core functionality works:
```bash
# After install, these should all work:
claude /help          # Shows installed commands
claude /scan          # Command exists
cat ~/.claude/skills/researcher/SKILL.md  # Skill exists
```

---

## Appendix: Research Sources

### Claude Code Documentation
- [Skills Documentation](https://code.claude.com/docs/en/skills.md)
- [Slash Commands Reference](https://code.claude.com/docs/en/slash-commands.md)
- [Settings Documentation](https://code.claude.com/docs/en/settings.md)
- [Hooks Reference](https://code.claude.com/docs/en/hooks.md)
- [Memory & CLAUDE.md](https://code.claude.com/docs/en/memory.md)

### Key Technical Details

**Skills:**
- Location: `~/.claude/skills/` (user) or `.claude/skills/` (project)
- Format: Directory with SKILL.md and optional supporting files
- Activation: Model-invoked based on description matching
- Frontmatter: name (required), description (required), allowed-tools (optional)

**Commands:**
- Location: `~/.claude/commands/` (user) or `.claude/commands/` (project)
- Format: Single .md file per command
- Activation: User-invoked with `/command-name`
- Frontmatter: description (required), allowed-tools, argument-hint, model (optional)

**Hooks:**
- Location: `~/.claude/hooks/` or configured in settings.json
- Format: Executable script (bash, python, etc.)
- Events: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SessionStart, etc.
- Exit codes: 0=success, 2=block, other=non-blocking error

**Settings:**
- Location: `~/.claude/settings.json` (user) or `.claude/settings.json` (project)
- Precedence: Enterprise > CLI args > Local > Shared > User
- Key sections: permissions, hooks, env, mcpServers

**Memory:**
- Location: `~/.claude/CLAUDE.md` (user) or `./CLAUDE.md` (project)
- Format: Plain markdown with optional @imports
- Purpose: Persistent instructions across sessions

---

## Next Steps

1. **Implement install-claude-config.sh** following this design
2. **Create config-registry.json** with all configs
3. **Test skill installation** end-to-end
4. **Add remaining components** (commands, hooks, settings)
5. **Add --force handling** for each category
6. **Write automated tests**
