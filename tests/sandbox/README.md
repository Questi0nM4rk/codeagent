# CodeAgent Test Sandbox

Isolated Docker-in-Docker (dind) testing environment for CodeAgent installation.

## Key Feature: Complete Isolation

All tests run inside Docker-in-Docker. This means:

- **Your host Docker is never touched**
- Infrastructure containers (Qdrant) run inside dind
- A-MEM uses local file storage (no container needed)
- When tests finish, `./test.sh --clean` removes everything
- No leftover containers, volumes, or configuration on your system

## Quick Start

```bash
cd tests/sandbox

# Run all tests (full integration)
./test.sh

# Run specific scenario
./test.sh source      # Quick lint check (fast)
./test.sh install     # Test installation only
./test.sh mcp         # Test MCP installation
./test.sh infra       # Test infrastructure

# Debug in container
./test.sh --shell

# Clean up everything
./test.sh --clean
```

## Test Scenarios

| Scenario  | Description                    | Time  |
| :-------- | :----------------------------- | :---- |
| `source`  | Shellcheck, file validation    | ~30s  |
| `install` | Full installation from GitHub  | ~3min |
| `mcp`     | MCP registration verification  | ~4min |
| `infra`   | Infrastructure startup/shutdown| ~5min |
| `cli`     | CLI command testing            | ~4min |
| `config`  | Config store/get operations    | ~4min |
| `all`     | All scenarios (default)        | ~10min|

## How It Works

```text
┌─────────────────────────────────────────────────────┐
│  Your Host System (completely untouched)            │
│                                                      │
│  ┌─────────────────────────────────────────────────┐│
│  │  Docker-in-Docker (dind)                        ││
│  │  - Has its own isolated Docker daemon           ││
│  │                                                 ││
│  │  ┌─────────────────────────────────────────┐   ││
│  │  │  Test Container                         │   ││
│  │  │  - Runs install.sh from GitHub          │   ││
│  │  │  - codeagent start → creates containers │   ││
│  │  │    inside dind, NOT on host             │   ││
│  │  └─────────────────────────────────────────┘   ││
│  │                                                 ││
│  │  ┌───────┐ ┌─────────────┐                     ││
│  │  │Qdrant │ │ A-MEM local │  ← Inside dind      ││
│  │  └───────┘ └─────────────┘                     ││
│  └─────────────────────────────────────────────────┘│
│                                                      │
│  docker compose down -v → Everything gone            │
└─────────────────────────────────────────────────────┘
```

## What Gets Tested

1. **Source Validation**
   - All shell scripts pass shellcheck
   - Required files exist and are executable
   - Skills, commands, agents are present

2. **Full Installation**
   - Curl one-liner from GitHub works
   - Directories created correctly
   - Symlinks in place
   - Python venv created

3. **MCP Installation**
   - All required MCPs registered (context7, reflection)
   - All optional MCPs registered (tavily, figma, supabase)
   - code-execution MCP registered (if Docker available)
   - Python MCPs importable

4. **Infrastructure**
   - Qdrant container starts
   - A-MEM uses local file storage
   - Services become healthy
   - A-MEM MCP registered
   - Clean shutdown

5. **CLI Commands**
   - All --help commands work
   - Config store/get round-trip

## Options

```bash
./test.sh [scenario] [options]

Options:
  --shell     Open interactive shell in container
  --rebuild   Force rebuild Docker image
  --clean     Clean up all test containers and volumes
  --verbose   Show verbose output
  --help      Show help
```

## Debugging

```bash
# Open shell in test environment
./test.sh --shell

# Inside container:
cd /home/testuser/codeagent-source
curl -fsSL https://raw.githubusercontent.com/.../install.sh | bash -s -- -y

# Check results
ls -la ~/.codeagent
ls -la ~/.claude
cat ~/.claude.json | jq .
docker ps  # Shows containers inside dind

# When done
exit
./test.sh --clean
```

## Fake API Keys

Tests use fake API keys to ensure all optional MCPs get installed:

- `OPENAI_API_KEY=sk-test-fake-key-for-testing-only`
- `TAVILY_API_KEY=tvly-test-fake-key-for-testing`
- `FIGMA_API_KEY=figd_test_fake_key_for_testing`
- `SUPABASE_ACCESS_TOKEN=sbp_test_fake_token_for_testing`

MCPs will register (which is what we test) but won't work at runtime (expected).

## CI Integration

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd tests/sandbox
          ./test.sh all
      - name: Cleanup
        if: always()
        run: |
          cd tests/sandbox
          ./test.sh --clean
```

## Architecture

```text
tests/sandbox/
├── docker-compose.yml   # dind + test services
├── Dockerfile           # Arch Linux test container
├── run-tests.sh         # Test runner (inside container)
├── test.sh              # Host convenience script
└── README.md            # This file
```
