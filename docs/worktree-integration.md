# Worktree Integration for Claude Code

This document describes the worktree management system that helps Claude Code work effectively across multiple parallel branches.

## Overview

The system uses [Worktrunk](https://worktrunk.dev) (`wt`) for worktree management, with a thin wrapper (`codeagent-wt`) that adds context awareness for Claude Code.

## Installation

```bash
# Install worktrunk
cargo install worktrunk

# Set up shell integration (allows wt switch to change directories)
wt config shell install
source ~/.zshrc  # or restart shell
```

## Quick Start

```bash
# Create a new worktree for a feature
codeagent-wt new feat/my-feature "Implement the new feature"

# List all worktrees with context
codeagent-wt list

# After creating a PR, update the context
codeagent-wt update-context

# Switch between worktrees
wt switch feat/my-feature
wt switch main

# Merge and cleanup when done
wt merge main
```

## Context File

Each worktree contains a `.worktree-context.json` file:

```json
{
  "branch": "feat/my-feature",
  "pr_number": 42,
  "pr_title": "feat: implement the new feature",
  "description": "Implement the new feature with tests",
  "task_id": "11",
  "created": "2026-02-05T18:00:00+00:00"
}
```

This file is read by the `worktree-context.sh` hook to inject context into Claude Code sessions.

## Hook Integration

The `framework/hooks/worktree-context.sh` hook outputs context when Claude is working in a worktree:

```text
<worktree-context>
📍 Worktree: /home/user/Projects/myrepo.feat-my-feature
   Branch: feat/my-feature
   PR: #42 - feat: implement the new feature
   Task: #11

   Implement the new feature with tests
</worktree-context>
```

## Commands

### codeagent-wt

| Command | Description |
|---------|-------------|
| `new <branch> [desc]` | Create worktree with context file |
| `update` | Update context with PR info from GitHub |
| `context` | Show current worktree context |
| `list` | List worktrees with context info |
| `<wt-command>` | Pass through to worktrunk |

### worktrunk (wt)

| Command | Description |
|---------|-------------|
| `wt switch <branch>` | Switch to worktree (changes directory) |
| `wt switch -c <branch>` | Create and switch to new worktree |
| `wt list` | List worktrees with status |
| `wt merge main` | Squash, rebase, merge, and cleanup |
| `wt remove` | Remove current worktree |

## Workflow Example

```bash
# 1. Create worktree for Epic 6
codeagent-wt new feat/epic6-consolidate "Consolidate MCPs into unified package"

# 2. Do your work...

# 3. Create PR
gh pr create --title "feat: consolidate MCPs" --body "..."

# 4. Update context with PR info
codeagent-wt update-context

# 5. After PR is merged, cleanup
wt merge main  # or wt remove if merged via GitHub
```

## Gitignore

Add `.worktree-context.json` to your `.gitignore` - it's local context, not committed.
