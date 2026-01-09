# CodeAgent Test Sandbox

Isolated Docker-based testing environment for CodeAgent installation scripts.

## Quick Start

```bash
cd tests/sandbox

# Run all tests
./test.sh

# Run specific scenario
./test.sh clean      # Test clean installation
./test.sh source     # Quick lint check (fastest)

# Debug in container
./test.sh --shell
```

## Test Scenarios

| Scenario | Description | Speed |
|----------|-------------|-------|
| `source` | Validate source files, shellcheck | Fast |
| `clean` | Full clean installation test | Medium |
| `cli` | Test CLI commands (--help, etc.) | Medium |
| `config` | Test config/keyring helpers | Medium |
| `marketplace` | Test marketplace commands | Medium |
| `upgrade` | Test upgrade over existing install | Medium |
| `force` | Test --force reinstall | Medium |
| `uninstall` | Test uninstall script | Medium |
| `all` | Run all scenarios | Slow |

## How It Works

1. **Dockerfile** creates an Arch Linux container with all dependencies
2. **Mock docker** commands simulate Docker (no daemon needed)
3. **run-tests.sh** executes test scenarios inside the container
4. **test.sh** provides a convenient host interface

## Architecture

```
tests/sandbox/
├── Dockerfile           # Arch Linux + deps + mock docker
├── docker-compose.yml   # Service definitions
├── test.sh              # Host convenience script
├── run-tests.sh         # Test runner (runs inside container)
└── README.md            # This file
```

## Options

```bash
./test.sh [scenario] [options]

Options:
  --shell     Open interactive shell in container
  --rebuild   Force rebuild Docker image
  --verbose   Show verbose output
  --help      Show help
```

## Example Output

```
╔═══════════════════════════════════════════════════════════╗
║           CodeAgent Installation Test Suite                ║
╚═══════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════
  Scenario 1: Source Code Validation
════════════════════════════════════════════════════════════

[PASS] install.sh exists
[PASS] install.sh is executable
[PASS] bin/codeagent exists
[PASS] shellcheck: install.sh
...

════════════════════════════════════════════════════════════
  Test Summary
════════════════════════════════════════════════════════════

  Passed:  42
  Failed:  0
  Skipped: 2
  Total:   44

╔═══════════════════════════════════════════════════════════╗
║                    ALL TESTS PASSED!                       ║
╚═══════════════════════════════════════════════════════════╝
```

## Debugging

Open a shell in the container:

```bash
./test.sh --shell

# Inside container:
cd /home/testuser/codeagent-source
./install.sh --no-docker -y

# Check results
ls -la ~/.codeagent
ls -la ~/.claude
codeagent --help
```

## CI Integration

For GitHub Actions:

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
```

## Notes

- Tests use mock Docker commands (no actual containers started)
- Network is disabled for isolation
- Source is mounted read-only to prevent accidental changes
- Uses non-root user for realistic testing
