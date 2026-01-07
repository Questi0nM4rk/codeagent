---
name: lua
description: Lua development expertise. Activates when working with .lua files or discussing Lua scripting, Neovim plugins, or game scripting.
---

# Lua Development Skill

Domain knowledge for Lua scripting and Neovim plugin development.

## Stack

- **Version**: Lua 5.4, LuaJIT
- **Testing**: busted, luaunit
- **Linting**: luacheck
- **Formatting**: stylua
- **Package Manager**: luarocks
- **LSP**: lua-language-server

## Commands

### Running

```bash
# Run script
lua script.lua
luajit script.lua

# Interactive REPL
lua
luajit

# With arguments
lua script.lua arg1 arg2
```

### Testing

```bash
# busted
busted
busted --filter="test name"
busted spec/
busted -o TAP

# luaunit
lua tests/test_module.lua
```

### Linting and Formatting

```bash
# luacheck
luacheck .
luacheck src/ --no-unused-args
luacheck . --config .luacheckrc

# stylua
stylua .
stylua --check .
stylua lua/ --config-path stylua.toml
```

### Package Management

```bash
# luarocks
luarocks install package
luarocks install --local package
luarocks list
luarocks make rockspec
```

## Patterns

### Module Pattern

```lua
local M = {}

-- Private
local function helper(x)
    return x * 2
end

-- Public
function M.process(data)
    return helper(data)
end

function M.setup(opts)
    opts = opts or {}
    M.config = vim.tbl_deep_extend("force", M.defaults, opts)
end

return M
```

### Class-like Pattern

```lua
local User = {}
User.__index = User

function User.new(name, email)
    local self = setmetatable({}, User)
    self.name = name
    self.email = email
    return self
end

function User:greet()
    return string.format("Hello, %s!", self.name)
end

return User
```

### Error Handling

```lua
-- pcall for protected calls
local ok, result = pcall(function()
    return risky_operation()
end)

if not ok then
    print("Error:", result)
    return nil
end

-- xpcall with traceback
local ok, result = xpcall(risky_operation, debug.traceback)
```

### Neovim Plugin Pattern

```lua
local M = {}

M.defaults = {
    enabled = true,
    keymaps = true,
}

function M.setup(opts)
    opts = vim.tbl_deep_extend("force", M.defaults, opts or {})

    if not opts.enabled then
        return
    end

    if opts.keymaps then
        M.setup_keymaps()
    end

    vim.api.nvim_create_autocmd("BufEnter", {
        callback = M.on_buf_enter,
    })
end

function M.setup_keymaps()
    vim.keymap.set("n", "<leader>x", M.action, { desc = "Plugin action" })
end

function M.action()
    -- plugin functionality
end

return M
```

### Iterators

```lua
-- pairs for tables with keys
for key, value in pairs(tbl) do
    print(key, value)
end

-- ipairs for arrays
for index, value in ipairs(arr) do
    print(index, value)
end

-- Custom iterator
local function range(from, to)
    local i = from - 1
    return function()
        i = i + 1
        if i <= to then return i end
    end
end

for i in range(1, 10) do
    print(i)
end
```

## Testing Patterns

### busted

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

### Mocking with busted

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

## Neovim-Specific

### API Patterns

```lua
-- Buffer operations
local buf = vim.api.nvim_get_current_buf()
local lines = vim.api.nvim_buf_get_lines(buf, 0, -1, false)
vim.api.nvim_buf_set_lines(buf, 0, -1, false, { "new content" })

-- Window operations
local win = vim.api.nvim_get_current_win()
local cursor = vim.api.nvim_win_get_cursor(win)

-- Create floating window
local buf = vim.api.nvim_create_buf(false, true)
local win = vim.api.nvim_open_win(buf, true, {
    relative = "editor",
    width = 50,
    height = 10,
    row = 5,
    col = 5,
    style = "minimal",
    border = "rounded",
})
```

### vim.fn and vim.cmd

```lua
-- Call Vim functions
local filename = vim.fn.expand("%:t")
local exists = vim.fn.filereadable(path) == 1

-- Execute Vim commands
vim.cmd("write")
vim.cmd([[
    highlight Normal guibg=none
    set number
]])
```

## Review Tools

```bash
# Lint
luacheck . --no-color

# Format check
stylua --check .

# Type checking (with lua-language-server annotations)
# Configured via .luarc.json
```

## File Organization

```
plugin/
├── lua/
│   └── plugin-name/
│       ├── init.lua
│       ├── config.lua
│       └── utils.lua
├── plugin/
│   └── plugin-name.lua
├── doc/
│   └── plugin-name.txt
└── spec/
    └── plugin_spec.lua
```

## Common Conventions

- Use local for all variables
- Prefer `and`/`or` for conditionals
- Use metatables for OOP patterns
- Check nil explicitly: `if x ~= nil then`
- Use `vim.tbl_extend` for table merging in Neovim
- Document with LuaLS annotations
