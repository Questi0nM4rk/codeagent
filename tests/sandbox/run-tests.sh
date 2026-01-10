#!/bin/bash
# ============================================
# CodeAgent Full Integration Test Runner
# Tests complete installation with real Docker (via dind)
# ============================================
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="/home/testuser/codeagent-source"
INSTALL_DIR="$HOME/.codeagent"
VERBOSE="${VERBOSE:-false}"
TEST_SCENARIO="${TEST_SCENARIO:-all}"

# GitHub install URL
GITHUB_RAW_URL="https://raw.githubusercontent.com/Questi0nM4rk/codeagent/main/install.sh"

# Note: Infrastructure tests are skipped in dind because:
# - Services started inside dind are only accessible from within dind
# - Test container can't reach localhost:6333 (Qdrant) or localhost:8283 (Letta)
# - Use ./test.sh --shell to manually test infrastructure if needed
SKIP_INFRA="${SKIP_INFRA:-true}"

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_skip() { echo -e "${YELLOW}[SKIP]${NC} $1"; }

log_header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# ============================================
# Test Utilities
# ============================================
assert_pass() {
    local desc="$1"
    log_success "$desc"
    ((++TESTS_PASSED)) || true
}

assert_fail() {
    local desc="$1"
    log_fail "$desc"
    ((++TESTS_FAILED)) || true
}

assert_file_exists() {
    local file="$1"
    local desc="${2:-$file exists}"
    if [ -f "$file" ]; then
        assert_pass "$desc"
        return 0
    else
        assert_fail "$desc (file not found: $file)"
        return 1
    fi
}

assert_dir_exists() {
    local dir="$1"
    local desc="${2:-$dir exists}"
    if [ -d "$dir" ]; then
        assert_pass "$desc"
        return 0
    else
        assert_fail "$desc (directory not found: $dir)"
        return 1
    fi
}

assert_executable() {
    local file="$1"
    local desc="${2:-$file is executable}"
    if [ -x "$file" ]; then
        assert_pass "$desc"
        return 0
    else
        assert_fail "$desc (not executable: $file)"
        return 1
    fi
}

assert_symlink() {
    local link="$1"
    local desc="${2:-$link is a symlink}"
    if [ -L "$link" ]; then
        assert_pass "$desc"
        return 0
    else
        assert_fail "$desc (not a symlink: $link)"
        return 1
    fi
}

assert_command_succeeds() {
    local cmd="$1"
    local desc="${2:-Command succeeds: $cmd}"
    if eval "$cmd" &>/dev/null; then
        assert_pass "$desc"
        return 0
    else
        assert_fail "$desc"
        return 1
    fi
}

assert_command_output_contains() {
    local cmd="$1"
    local expected="$2"
    local desc="${3:-Output contains: $expected}"
    local output
    output=$(eval "$cmd" 2>&1 || true)
    if echo "$output" | grep -q "$expected"; then
        assert_pass "$desc"
        return 0
    else
        assert_fail "$desc (output: ${output:0:200})"
        return 1
    fi
}

assert_shellcheck_passes() {
    local file="$1"
    local desc="${2:-shellcheck: $(basename "$file")}"
    if command -v shellcheck &>/dev/null; then
        if shellcheck -e SC2034,SC2155,SC2086,SC1090,SC2015,SC2129,SC2016,SC2012,SC2164 -S warning "$file" 2>/dev/null; then
            assert_pass "$desc"
            return 0
        else
            assert_fail "$desc"
            return 1
        fi
    else
        log_skip "$desc (shellcheck not available)"
        ((++TESTS_SKIPPED)) || true
        return 0
    fi
}

# ============================================
# Cleanup Functions
# ============================================
cleanup_installation() {
    log_info "Cleaning up previous installation..."
    rm -rf "$HOME/.codeagent" 2>/dev/null || true
    rm -rf "$HOME/.claude" 2>/dev/null || true
    rm -f "$HOME/.claude.json" 2>/dev/null || true
    rm -f "$HOME/.local/bin/codeagent"* 2>/dev/null || true
    sed -i '/CODEAGENT_HOME/d' "$HOME/.bashrc" 2>/dev/null || true
    sed -i '/# CodeAgent/d' "$HOME/.bashrc" 2>/dev/null || true

    # Stop any running containers (inside dind)
    docker ps -q 2>/dev/null | xargs -r docker stop 2>/dev/null || true
    docker ps -aq 2>/dev/null | xargs -r docker rm -f 2>/dev/null || true
}

# ============================================
# Test Scenarios
# ============================================

# Scenario 1: Source Code Validation
test_source_code() {
    log_header "Scenario 1: Source Code Validation"

    log_info "Checking source files exist and pass linting..."

    assert_file_exists "$SOURCE_DIR/install.sh" "install.sh exists"
    assert_executable "$SOURCE_DIR/install.sh" "install.sh is executable"

    for script in codeagent codeagent-start codeagent-stop codeagent-status codeagent-config codeagent-marketplace; do
        assert_file_exists "$SOURCE_DIR/bin/$script" "bin/$script exists"
        assert_executable "$SOURCE_DIR/bin/$script" "bin/$script is executable"
    done

    log_info "Running shellcheck on scripts..."
    assert_shellcheck_passes "$SOURCE_DIR/install.sh"

    for script in "$SOURCE_DIR"/bin/*; do
        if [ -f "$script" ]; then
            assert_shellcheck_passes "$script"
        fi
    done

    log_info "Checking skills..."
    local skill_count
    skill_count=$(find "$SOURCE_DIR/framework/skills" -name "SKILL.md" 2>/dev/null | wc -l)
    if [ "$skill_count" -ge 15 ]; then
        assert_pass "Skills found: $skill_count"
    else
        assert_fail "Expected at least 15 skills, found: $skill_count"
    fi

    local cmd_count
    cmd_count=$(find "$SOURCE_DIR/framework/commands" -name "*.md" 2>/dev/null | wc -l)
    if [ "$cmd_count" -ge 5 ]; then
        assert_pass "Commands found: $cmd_count"
    else
        assert_fail "Expected at least 5 commands, found: $cmd_count"
    fi

    log_info "Checking agents..."
    local agent_count
    agent_count=$(find "$SOURCE_DIR/framework/agents" -name "*.md" 2>/dev/null | wc -l)
    if [ "$agent_count" -ge 6 ]; then
        assert_pass "Agents found: $agent_count"
    else
        assert_fail "Expected at least 6 agents, found: $agent_count"
    fi
}

# Scenario 2: Full Installation with Docker
test_full_install() {
    log_header "Scenario 2: Full Installation (with Docker via dind)"

    cleanup_installation

    # Verify Docker (dind) is accessible
    log_info "Verifying Docker (dind) connection..."
    if docker info &>/dev/null; then
        assert_pass "Docker (dind) is accessible"
    else
        assert_fail "Docker (dind) not accessible - DOCKER_HOST=$DOCKER_HOST"
        return 1
    fi

    # Run full installation from GitHub
    # Note: --no-docker because infrastructure inside dind isn't accessible from test container
    log_info "Installing via curl one-liner from GitHub..."
    local log_file="/tmp/install-$$.log"
    local install_flags="-y"

    if [ "$SKIP_INFRA" = "true" ]; then
        install_flags="-y --no-docker"
        log_info "Using --no-docker flag (infrastructure tests skipped in dind)"
    fi

    if curl -fsSL "$GITHUB_RAW_URL" | bash -s -- $install_flags 2>&1 | tee "$log_file"; then
        assert_pass "Installation completed without errors"
    else
        assert_fail "Installation script failed"
        [ "$VERBOSE" = "true" ] && cat "$log_file"
        return 1
    fi

    # Verify installation directories
    log_info "Verifying installation directories..."
    assert_dir_exists "$INSTALL_DIR" "Install directory created"
    assert_dir_exists "$HOME/.claude" "Claude config directory"
    assert_dir_exists "$HOME/.claude/skills" "Skills directory"
    assert_dir_exists "$HOME/.claude/commands" "Commands directory"
    assert_dir_exists "$HOME/.claude/hooks" "Hooks directory"
    assert_dir_exists "$HOME/.claude/agents" "Agents directory"

    # Verify bin symlinks
    for script in codeagent codeagent-start codeagent-stop codeagent-status codeagent-config codeagent-marketplace; do
        assert_symlink "$HOME/.local/bin/$script" "Symlink: $script"
    done

    # Verify core agents installed
    log_info "Checking installed agents..."
    for agent in researcher architect orchestrator implementer reviewer learner; do
        assert_file_exists "$HOME/.claude/agents/$agent.md" "Agent: $agent installed"
    done

    # Check Python venv
    assert_dir_exists "$INSTALL_DIR/venv" "Python venv created"
    assert_executable "$INSTALL_DIR/venv/bin/python" "venv Python executable"
}

# Scenario 3: MCP Installation Verification
test_mcp_installation() {
    log_header "Scenario 3: MCP Installation Verification"

    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    # Check that claude CLI has MCPs registered
    log_info "Checking MCP registrations in claude.json..."

    local claude_json="$HOME/.claude.json"
    if [ -f "$claude_json" ]; then
        assert_pass "claude.json exists"

        # Check required MCPs
        local required_mcps=("context7" "reflection")
        for mcp in "${required_mcps[@]}"; do
            if grep -q "\"$mcp\"" "$claude_json"; then
                assert_pass "MCP registered: $mcp"
            else
                assert_fail "MCP not registered: $mcp"
            fi
        done

        # Check optional MCPs (should be installed with fake keys)
        local optional_mcps=("tavily" "figma" "supabase")
        for mcp in "${optional_mcps[@]}"; do
            if grep -q "\"$mcp\"" "$claude_json"; then
                assert_pass "Optional MCP registered: $mcp"
            else
                assert_fail "Optional MCP not registered: $mcp (API key may not have worked)"
            fi
        done

        # Check uvx MCPs (code-execution)
        if grep -q "code-execution" "$claude_json"; then
            assert_pass "MCP registered: code-execution"
        else
            assert_fail "MCP not registered: code-execution"
        fi
    else
        assert_fail "claude.json not found"
    fi

    # Verify Python MCPs can be imported
    log_info "Verifying Python MCPs can be imported..."
    local venv_python="$INSTALL_DIR/venv/bin/python"

    if $venv_python -c "import reflection_mcp" 2>/dev/null; then
        assert_pass "Python MCP importable: reflection"
    else
        assert_fail "Python MCP not importable: reflection"
    fi
}

# Scenario 4: Infrastructure Startup
test_infrastructure() {
    log_header "Scenario 4: Infrastructure Startup"

    if [ "$SKIP_INFRA" = "true" ]; then
        log_warn "Infrastructure tests SKIPPED (dind limitation)"
        log_info "Services inside dind aren't accessible from test container"
        log_info "To test infrastructure manually: ./test.sh --shell"
        ((++TESTS_SKIPPED)) || true
        return 0
    fi

    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    # Start infrastructure
    log_info "Starting CodeAgent infrastructure (Qdrant, Letta)..."

    if timeout 180 "$HOME/.local/bin/codeagent-start" 2>&1 | tee /tmp/infra-start.log; then
        assert_pass "Infrastructure startup command succeeded"
    else
        log_warn "Infrastructure startup had issues (may be expected in dind)"
        [ "$VERBOSE" = "true" ] && cat /tmp/infra-start.log
    fi

    # Wait for containers to be ready
    log_info "Waiting for containers to be healthy..."
    sleep 30

    # Check if containers are running
    log_info "Checking container status..."

    if docker ps --format '{{.Names}}' | grep -q "codeagent-qdrant"; then
        assert_pass "Container running: qdrant"
    else
        assert_fail "Container not running: qdrant"
    fi

    if docker ps --format '{{.Names}}' | grep -q "codeagent-letta"; then
        assert_pass "Container running: letta"
    else
        assert_fail "Container not running: letta"
    fi

    # Check service health via codeagent status
    log_info "Checking service health..."
    if "$HOME/.local/bin/codeagent-status" 2>&1 | grep -q "healthy\|running"; then
        assert_pass "Services report healthy status"
    else
        log_warn "Services may not be fully healthy (checking individually)"
    fi

    # Verify Letta MCP registration (requires running Letta)
    log_info "Checking Letta MCP registration..."
    local claude_json="$HOME/.claude.json"
    if grep -q "\"letta\"" "$claude_json" 2>/dev/null; then
        assert_pass "MCP registered: letta"
    else
        assert_fail "MCP not registered: letta"
    fi
}

# Scenario 5: CLI Commands
test_cli_commands() {
    log_header "Scenario 5: CLI Commands"

    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    log_info "Testing CLI --help commands..."

    assert_command_output_contains "$HOME/.local/bin/codeagent --help" "Usage" "codeagent --help shows usage"
    assert_command_output_contains "$HOME/.local/bin/codeagent-config --help" "Usage" "codeagent-config --help shows usage"
    assert_command_output_contains "$HOME/.local/bin/codeagent-marketplace --help" "Usage" "codeagent-marketplace --help shows usage"
    assert_command_output_contains "$HOME/.local/bin/codeagent-status --help" "Usage" "codeagent-status --help shows usage"

    log_info "Testing codeagent subcommands..."
    assert_command_output_contains "$HOME/.local/bin/codeagent config --help" "store" "codeagent config has store command"
    assert_command_output_contains "$HOME/.local/bin/codeagent marketplace --help" "search" "codeagent marketplace has search command"
}

# Scenario 6: Config Store/Get
test_config_operations() {
    log_header "Scenario 6: Config Store/Get Operations"

    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    # Test store and get (using .env fallback in container)
    log_info "Testing config store/get..."

    "$HOME/.local/bin/codeagent-config" store TEST_KEY "test_value_123" 2>/dev/null || true

    local retrieved
    retrieved=$("$HOME/.local/bin/codeagent-config" get TEST_KEY 2>/dev/null || echo "NOT_FOUND")

    if [ "$retrieved" = "test_value_123" ]; then
        assert_pass "Config store/get round-trip works"
    else
        assert_fail "Config store/get failed (got: $retrieved)"
    fi
}

# Scenario 7: Infrastructure Shutdown
test_infrastructure_stop() {
    log_header "Scenario 7: Infrastructure Shutdown"

    if [ "$SKIP_INFRA" = "true" ]; then
        log_warn "Infrastructure stop test SKIPPED (dind limitation)"
        ((++TESTS_SKIPPED)) || true
        return 0
    fi

    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

    log_info "Stopping infrastructure..."

    if "$HOME/.local/bin/codeagent-stop" 2>&1; then
        assert_pass "Infrastructure stop command succeeded"
    else
        log_warn "Infrastructure stop had issues"
    fi

    # Verify containers stopped
    sleep 5

    local running
    running=$(docker ps --format '{{.Names}}' | grep -c "codeagent-" || echo "0")

    if [ "$running" -eq 0 ]; then
        assert_pass "All CodeAgent containers stopped"
    else
        assert_fail "Some containers still running: $running"
    fi
}

# ============================================
# Summary
# ============================================
print_summary() {
    log_header "Test Summary"

    local total=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

    echo -e "  ${GREEN}Passed:${NC}  $TESTS_PASSED"
    echo -e "  ${RED}Failed:${NC}  $TESTS_FAILED"
    echo -e "  ${YELLOW}Skipped:${NC} $TESTS_SKIPPED"
    echo -e "  ${CYAN}Total:${NC}   $total"
    echo ""

    if [ "$TESTS_FAILED" -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                    ALL TESTS PASSED!                       ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
        return 0
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    SOME TESTS FAILED                       ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
        return 1
    fi
}

# ============================================
# Main
# ============================================
main() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        CodeAgent Full Integration Test Suite              ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    log_info "Source directory: $SOURCE_DIR"
    log_info "Install directory: $INSTALL_DIR"
    log_info "Test scenario: $TEST_SCENARIO"
    log_info "Docker host: ${DOCKER_HOST:-local}"

    case "$TEST_SCENARIO" in
        source)
            test_source_code
            ;;
        install)
            test_source_code
            test_full_install
            ;;
        mcp)
            test_full_install
            test_mcp_installation
            ;;
        infra)
            test_full_install
            test_infrastructure
            test_infrastructure_stop
            ;;
        cli)
            test_full_install
            test_cli_commands
            ;;
        config)
            test_full_install
            test_config_operations
            ;;
        all|*)
            test_source_code
            test_full_install
            test_mcp_installation
            test_infrastructure
            test_cli_commands
            test_config_operations
            test_infrastructure_stop
            ;;
    esac

    print_summary
}

main "$@"
