---
name: lua
description: Lua development expertise. Activates when working with .lua files or discussing Lua scripting, Neovim plugins, or game scripting.
---

# Lua Development Skill

Domain knowledge for Lua scripting and Neovim plugin development.

## The Iron Law

```text
LOCAL EVERYTHING + LUACHECK CLEAN + STYLUA FORMATTED
All variables are local. luacheck passes. stylua --check passes.
```

## Core Principle

> "Global is evil. Local is fast. Type annotations catch bugs before runtime."

## When to Use

**Always:**

- Writing Lua scripts or modules
- Developing Neovim plugins
- Working with game scripting (Love2D, Defold)
- Creating Lua-based configurations

**Exceptions (ask human partner):**

- Legacy codebases without luacheck
- Embedded Lua with constrained environments

## Stack

| Component       | Technology             |
| :-------------- | :--------------------- |
| Version         | Lua 5.4, LuaJIT        |
| Testing         | busted, luaunit        |
| Linting         | luacheck               |
| Formatting      | stylua                 |
| Package Manager | luarocks               |
| LSP             | lua-language-server    |

## Essential Commands

```bash
# Run scripts
lua script.lua
luajit script.lua

# Test
busted
busted --filter="test name"

# Lint + format
luacheck . --config .luacheckrc
stylua . && stylua --check .
```

## Patterns

### Module Pattern

### Good Example: Module with Local Functions

```lua
local M = {}

--- Private helper (local function)
local function helper(x)
    return x * 2
end

--- Process data with transformation
---@param data number
---@return number
function M.process(data)
    return helper(data)
end

---@param opts table|nil
function M.setup(opts)
    opts = opts or {}
    M.config = vim.tbl_deep_extend("force", M.defaults, opts)
end

return M
```

- All functions local or namespaced to M
- LuaLS annotations for types
- Explicit nil handling with `or {}`

### Bad Example: Global Functions

```lua
function process(data)
    return data * 2
end

helper = function(x) return x end
```

- Global functions pollute namespace
- No type annotations
- Hard to test and maintain

### Class-like Pattern

### Good Example: Class with Metatables

```lua
---@class User
---@field name string
---@field email string
local User = {}
User.__index = User

---@param name string
---@param email string
---@return User
function User.new(name, email)
    local self = setmetatable({}, User)
    self.name = name
    self.email = email
    return self
end

---@return string
function User:greet()
    return string.format("Hello, %s!", self.name)
end

return User
```

- LuaLS class annotations
- Proper metatable usage
- Method uses `:` (implicit self)

### Error Handling

```lua
-- pcall for protected calls
local ok, result = pcall(function()
    return risky_operation()
end)

if not ok then
    vim.notify("Error: " .. result, vim.log.levels.ERROR)
    return nil
end

-- xpcall with traceback for debugging
local ok, result = xpcall(risky_operation, debug.traceback)
```

### Neovim Plugin Pattern

```lua
local M = {}

M.defaults = {
    enabled = true,
    keymaps = true,
}

---@param opts table|nil
function M.setup(opts)
    opts = vim.tbl_deep_extend("force", M.defaults, opts or {})

    if not opts.enabled then return end

    if opts.keymaps then
        M.setup_keymaps()
    end

    vim.api.nvim_create_autocmd("BufEnter", {
        callback = M.on_buf_enter,
    })
end

return M
```

## Testing Patterns

### busted

### Good Example: busted Test Suite

```lua
describe("User", function()
    local User

    before_each(function()
        User = require("user")
    end)

    describe("new", function()
        it("creates a user with name", function()
            local user = User.new("John", "john@example.com")
            assert.are.equal("John", user.name)
        end)
    end)

    describe("greet", function()
        it("returns greeting message", function()
            local user = User.new("John", "john@example.com")
            assert.are.equal("Hello, John!", user:greet())
        end)
    end)
end)
```

- Descriptive nested structure
- Setup in before_each
- Clear assertion messages

### Mocking

```lua
describe("Service", function()
    it("calls repository", function()
        local mock_repo = {
            get = spy.new(function() return { id = 1 } end)
        }

        local service = Service.new(mock_repo)
        service:find(1)

        assert.spy(mock_repo.get).was_called_with(1)
    end)
end)
```

## Common Rationalizations

| Excuse | Reality |
| :----- | :------ |
| "Globals are easier" | They cause bugs. Local is 30% faster. |
| "luacheck is too strict" | It catches real bugs. Configure it properly. |
| "Types are optional" | Annotations prevent runtime errors. Add them. |
| "It's just a small script" | Small scripts become big scripts. Do it right. |

## Red Flags - STOP

- Global variables (missing `local`)
- No `return M` at module end
- `function M.method(self, ...)` instead of `function M:method(...)`
- Missing nil checks before table access
- `require` inside loops
- No LuaLS annotations on public functions

If you see these, stop and fix before continuing.

## Verification Checklist

- [ ] `luacheck .` passes clean
- [ ] `stylua --check .` passes
- [ ] All variables/functions are local
- [ ] Module returns table at end
- [ ] Public functions have LuaLS annotations
- [ ] Tests pass with `busted`
- [ ] No global namespace pollution

## Review Tools

```bash
luacheck . --no-color              # Lint
stylua --check .                   # Format check
lua-language-server --check .      # Type check (configured via .luarc.json)
busted --coverage                  # Tests with coverage
```

## When Stuck

| Problem | Solution |
| :------ | :------- |
| "undefined global" warning | Add `local` or configure `.luacheckrc` for vim globals |
| Circular require | Move shared code to separate module |
| Metatable confusion | Use `__index = ClassName` pattern consistently |
| vim API not found | Ensure running in Neovim context, mock for tests |

## Related Skills

- `neovim` - Neovim-specific APIs and patterns
- `tdd` - Test-first development workflow
- `reviewer` - Uses luacheck/stylua for validation
