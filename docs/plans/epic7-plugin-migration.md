# Epic 7: Migrate Skills and Commands to Plugin Format

## Status: Not Started (blocked by Epic 6)

## Goal

Move 18 skills and 7 commands from `claude-project/framework/` to `codeagent/` plugin structure. Update tool references to match unified MCP tool names.

## Scope

- Move skills to `codeagent/skills/{languages,methodologies,workflow}/`
- Move commands to `codeagent/commands/`
- Update all tool references (36 old names -> 15 new names)
- Update trigger patterns for plugin system
- Preserve existing behavior

## Depends On

- Epic 6 (unified MCP must be running for tool name updates)

## Details

TBD after Epic 6 is complete.
