# Worktree Integration - Future Enhancements

Ideas that go beyond the POC scope. Implement after POC is validated.

## Task Integration

**Priority**: High

Link worktrees to the task system:

- `codeagent-wt new` accepts `--task <id>` flag
- Automatically updates task metadata with worktree path
- `TaskList` shows worktree paths for each task
- When task is completed, prompt to cleanup worktree

```bash
codeagent-wt new feat/epic6 --task 11
# Updates task #11 with worktree path
```

## CI/PR Status in List

**Priority**: High

Show CI status and review state in `codeagent-wt list`:

```text
  Branch                    PR     CI       Review     Description
  feat/epic6                #12    ✅ pass  ⏳ pending  Consolidate MCPs
  feat/epic7                #13    🔄 run   ❌ changes  Plugin format
```

Requires: `gh pr view` integration, caching for performance

## Auto-create Context on wt switch

**Priority**: Medium

Hook into `wt switch --create` to automatically create `.worktree-context.json`:

- Post-create hook in worktrunk config
- Or shell function wrapper

## Session State Persistence

**Priority**: Medium

Remember which worktree Claude was last in:

- Store in `~/.claude/session-state.json`
- On session resume, show context of last worktree
- Auto-suggest returning to it

## Auto-cleanup on PR Merge

**Priority**: Low

Webhook or polling to detect merged PRs:

- When PR is merged, notify user
- Offer to run `wt remove` automatically
- Update task status to completed

## Worktree Templates

**Priority**: Low

Pre-configured worktree setups:

- Copy specific files (`.env.example` → `.env`)
- Run setup commands (`npm install`, `uv sync`)
- Configure via `.worktree-templates.yaml`

## Multi-repo Worktree Dashboard

**Priority**: Low

Global command to see all worktrees across all repos:

```bash
codeagent worktrees --global
# Shows worktrees from all repos in ~/Projects/
```

## Integration with /plan

**Priority**: Medium

When `/plan` detects parallel tasks:

- Auto-suggest creating worktrees
- Generate worktree creation commands
- Link planned tasks to worktrees

---

_Add new ideas here as they come up during development._
