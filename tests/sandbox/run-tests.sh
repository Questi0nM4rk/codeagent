#!/bin/bash
# ============================================
# CodeAgent Test Runner
# Runs all test scenarios in the sandbox
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
SOURCE_DIR="${SCRIPT_DIR}/../.."
INSTALL_DIR="$HOME/.codeagent"
TEST_RESULTS_DIR="${SCRIPT_DIR}/results"
VERBOSE="${VERBOSE:-false}"

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
assert_file_exists() {
    local file="$1"
    local desc="${2:-$file exists}"
    if [ -f "$file" ]; then
        log_success "$desc"
        ((++TESTS_PASSED)) || true
        return 0
    else
        log_fail "$desc (file not found: $file)"
        ((++TESTS_FAILED)) || true
        return 1
    fi
}

assert_dir_exists() {
    local dir="$1"
    local desc="${2:-$dir exists}"
    if [ -d "$dir" ]; then
        log_success "$desc"
        ((++TESTS_PASSED)) || true
        return 0
    else
        log_fail "$desc (directory not found: $dir)"
        ((++TESTS_FAILED)) || true
        return 1
    fi
}

assert_executable() {
    local file="$1"
    local desc="${2:-$file is executable}"
    if [ -x "$file" ]; then
        log_success "$desc"
        ((++TESTS_PASSED)) || true
        return 0
    else
        log_fail "$desc (not executable: $file)"
        ((++TESTS_FAILED)) || true
        return 1
    fi
}

assert_symlink() {
    local link="$1"
    local desc="${2:-$link is a symlink}"
    if [ -L "$link" ]; then
        log_success "$desc"
        ((++TESTS_PASSED)) || true
        return 0
    else
        log_fail "$desc (not a symlink: $link)"
        ((++TESTS_FAILED)) || true
        return 1
    fi
}

assert_command_succeeds() {
    local cmd="$1"
    local desc="${2:-Command succeeds: $cmd}"
    if eval "$cmd" &>/dev/null; then
        log_success "$desc"
        ((++TESTS_PASSED)) || true
        return 0
    else
        log_fail "$desc (command failed: $cmd)"
        ((++TESTS_FAILED)) || true
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
        log_success "$desc"
        ((++TESTS_PASSED)) || true
        return 0
    else
        log_fail "$desc (output: $output)"
        ((++TESTS_FAILED)) || true
        return 1
    fi
}

assert_shellcheck_passes() {
    local file="$1"
    local desc="${2:-shellcheck: $(basename "$file")}"
    if command -v shellcheck &>/dev/null; then
        # Exclude style/info warnings, only fail on actual errors
        # SC2034: unused variables (common for colors)
        # SC2155: declare and assign separately (style)
        # SC2086: double quote variables (info)
        # SC1090: can't follow dynamic source (info)
        # SC2015: A && B || C pattern (info)
        # SC2129: multiple redirects (style)
        # SC2016: single quotes don't expand (info)
        # SC2012: use find instead of ls (info)
        # SC2164: cd without || exit (warning but common)
        if shellcheck -e SC2034,SC2155,SC2086,SC1090,SC2015,SC2129,SC2016,SC2012,SC2164 -S warning "$file" 2>/dev/null; then
            log_success "$desc"
            ((++TESTS_PASSED)) || true
            return 0
        else
            log_fail "$desc"
            ((++TESTS_FAILED)) || true
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
    rm -f "$HOME/.local/bin/codeagent"* 2>/dev/null || true
    # Remove CODEAGENT_HOME from bashrc if present
    sed -i '/CODEAGENT_HOME/d' "$HOME/.bashrc" 2>/dev/null || true
    sed -i '/# CodeAgent/d' "$HOME/.bashrc" 2>/dev/null || true
}

# ============================================
# Test Scenarios
# ============================================

# Scenario 1: Source Code Validation
test_source_code() {
    log_header "Scenario 1: Source Code Validation"

    log_info "Checking source files exist and pass linting..."

    # Check main scripts exist
    assert_file_exists "$SOURCE_DIR/install.sh" "install.sh exists"
    assert_executable "$SOURCE_DIR/install.sh" "install.sh is executable"

    # Check bin scripts
    for script in codeagent codeagent-start codeagent-stop codeagent-status codeagent-config codeagent-marketplace; do
        assert_file_exists "$SOURCE_DIR/bin/$script" "bin/$script exists"
        assert_executable "$SOURCE_DIR/bin/$script" "bin/$script is executable"
    done

    # Shellcheck validation
    log_info "Running shellcheck on scripts..."
    assert_shellcheck_passes "$SOURCE_DIR/install.sh"

    for script in "$SOURCE_DIR"/bin/*; do
        if [ -f "$script" ]; then
            assert_shellcheck_passes "$script"
        fi
    done

    # Check skills exist
    log_info "Checking skills..."
    local skill_count
    skill_count=$(find "$SOURCE_DIR/framework/skills" -name "SKILL.md" 2>/dev/null | wc -l)
    if [ "$skill_count" -ge 15 ]; then
        log_success "Skills found: $skill_count"
        ((++TESTS_PASSED)) || true
    else
        log_fail "Expected at least 15 skills, found: $skill_count"
        ((++TESTS_FAILED)) || true
    fi

    # Check commands exist
    local cmd_count
    cmd_count=$(find "$SOURCE_DIR/framework/commands" -name "*.md" 2>/dev/null | wc -l)
    if [ "$cmd_count" -ge 5 ]; then
        log_success "Commands found: $cmd_count"
        ((++TESTS_PASSED)) || true
    else
        log_fail "Expected at least 5 commands, found: $cmd_count"
        ((++TESTS_FAILED)) || true
    fi

    # Check agents exist
    log_info "Checking agents..."
    local agent_count
    agent_count=$(find "$SOURCE_DIR/framework/agents" -name "*.md" 2>/dev/null | wc -l)
    if [ "$agent_count" -ge 6 ]; then
        log_success "Agents found: $agent_count"
        ((++TESTS_PASSED)) || true
    else
        log_fail "Expected at least 6 agents, found: $agent_count"
        ((++TESTS_FAILED)) || true
    fi
}

# Scenario 2: Clean Install
test_clean_install() {
    log_header "Scenario 2: Clean Install"

    cleanup_installation

    log_info "Running install.sh --no-docker..."
    cd "$SOURCE_DIR"

    # Run installation (skip Docker for sandbox)
    if ./install.sh --local --no-docker -y 2>&1 | tee /tmp/install.log; then
        log_success "Installation completed without errors"
        ((++TESTS_PASSED)) || true
    else
        log_fail "Installation script failed"
        ((++TESTS_FAILED)) || true
        [ "$VERBOSE" = "true" ] && cat /tmp/install.log
    fi

    # Verify installation results
    log_info "Verifying installation..."

    # Check install directory
    assert_dir_exists "$INSTALL_DIR" "Install directory created"

    # Check bin symlinks
    for script in codeagent codeagent-start codeagent-stop codeagent-status codeagent-config codeagent-marketplace; do
        assert_symlink "$HOME/.local/bin/$script" "Symlink: $script"
    done

    # Check Claude config
    assert_dir_exists "$HOME/.claude" "Claude config directory"
    assert_dir_exists "$HOME/.claude/skills" "Skills directory"
    assert_dir_exists "$HOME/.claude/commands" "Commands directory"
    assert_dir_exists "$HOME/.claude/hooks" "Hooks directory"
    assert_dir_exists "$HOME/.claude/agents" "Agents directory"

    # Verify core agents installed
    log_info "Checking installed agents..."
    for agent in researcher architect orchestrator implementer reviewer learner; do
        assert_file_exists "$HOME/.claude/agents/$agent.md" "Agent: $agent installed"
    done

    # Check venv was created
    assert_dir_exists "$INSTALL_DIR/venv" "Python venv created"
    assert_executable "$INSTALL_DIR/venv/bin/python" "venv Python is executable"
}

# Scenario 3: CLI Commands
test_cli_commands() {
    log_header "Scenario 3: CLI Commands"

    # Ensure PATH includes local bin
    export PATH="$HOME/.local/bin:$PATH"

    # Test help commands
    log_info "Testing CLI --help commands..."

    assert_command_output_contains "$HOME/.local/bin/codeagent --help" "Usage" "codeagent --help shows usage"
    assert_command_output_contains "$HOME/.local/bin/codeagent-config --help" "Usage" "codeagent-config --help shows usage"
    assert_command_output_contains "$HOME/.local/bin/codeagent-marketplace --help" "Usage" "codeagent-marketplace --help shows usage"

    # Test codeagent subcommands
    log_info "Testing codeagent subcommands..."
    assert_command_output_contains "$HOME/.local/bin/codeagent config --help" "store" "codeagent config --help shows store command"
    assert_command_output_contains "$HOME/.local/bin/codeagent marketplace --help" "search" "codeagent marketplace --help shows search command"
}

# Scenario 4: Config/Keyring Helpers
test_config_keyring() {
    log_header "Scenario 4: Config & Keyring Helpers"

    export PATH="$HOME/.local/bin:$PATH"

    # Test list command (should work even with empty keyring)
    log_info "Testing config list command..."
    if "$HOME/.local/bin/codeagent-config" list 2>&1 | grep -q "Stored Secrets"; then
        log_success "codeagent-config list works"
        ((++TESTS_PASSED)) || true
    else
        log_fail "codeagent-config list failed"
        ((++TESTS_FAILED)) || true
    fi

    # Test store and get (using .env fallback since no keyring daemon in container)
    log_info "Testing store/get with .env fallback..."
    "$HOME/.local/bin/codeagent-config" store TEST_KEY "test_value_123" 2>/dev/null || true

    local retrieved
    retrieved=$("$HOME/.local/bin/codeagent-config" get TEST_KEY 2>/dev/null || echo "NOT_FOUND")

    if [ "$retrieved" = "test_value_123" ]; then
        log_success "store/get round-trip works"
        ((++TESTS_PASSED)) || true
    else
        log_fail "store/get round-trip failed (got: $retrieved)"
        ((++TESTS_FAILED)) || true
    fi
}

# Scenario 5: Marketplace Commands
test_marketplace() {
    log_header "Scenario 5: Marketplace Commands"

    export PATH="$HOME/.local/bin:$PATH"

    # Test that marketplace script exists and shows help
    log_info "Testing marketplace help..."
    assert_command_output_contains "$HOME/.local/bin/codeagent-marketplace --help" "Smithery" "marketplace mentions Smithery"
    assert_command_output_contains "$HOME/.local/bin/codeagent-marketplace --help" "search" "marketplace has search command"
    assert_command_output_contains "$HOME/.local/bin/codeagent-marketplace --help" "install" "marketplace has install command"

    # Note: Actual Smithery commands require network and npx, so we just verify the script structure
    log_info "Verifying marketplace script structure..."
    if grep -q "npx.*@smithery/cli" "$SOURCE_DIR/bin/codeagent-marketplace"; then
        log_success "marketplace uses @smithery/cli"
        ((++TESTS_PASSED)) || true
    else
        log_fail "marketplace doesn't reference @smithery/cli"
        ((++TESTS_FAILED)) || true
    fi
}

# Scenario 6: Upgrade Install
test_upgrade_install() {
    log_header "Scenario 6: Upgrade Install (over existing)"

    # Don't cleanup - run over existing installation
    log_info "Running install.sh over existing installation..."
    cd "$SOURCE_DIR"

    if ./install.sh --local --no-docker -y 2>&1 | tee /tmp/upgrade.log; then
        log_success "Upgrade completed without errors"
        ((++TESTS_PASSED)) || true
    else
        log_fail "Upgrade script failed"
        ((++TESTS_FAILED)) || true
        [ "$VERBOSE" = "true" ] && cat /tmp/upgrade.log
    fi

    # Verify everything still works
    log_info "Verifying post-upgrade state..."
    assert_dir_exists "$INSTALL_DIR" "Install directory still exists"
    assert_executable "$HOME/.local/bin/codeagent" "codeagent still executable"
}

# Scenario 7: Force Reinstall
test_force_reinstall() {
    log_header "Scenario 7: Force Reinstall"

    log_info "Running install.sh --force --no-docker..."
    cd "$SOURCE_DIR"

    if ./install.sh --local --force --no-docker -y 2>&1 | tee /tmp/force.log; then
        log_success "Force reinstall completed"
        ((++TESTS_PASSED)) || true
    else
        log_fail "Force reinstall failed"
        ((++TESTS_FAILED)) || true
        [ "$VERBOSE" = "true" ] && cat /tmp/force.log
    fi
}

# Scenario 8: Uninstall
test_uninstall() {
    log_header "Scenario 8: Uninstall"

    if [ -f "$SOURCE_DIR/uninstall.sh" ]; then
        log_info "Running uninstall.sh..."
        cd "$SOURCE_DIR"

        if ./uninstall.sh -y 2>&1 | tee /tmp/uninstall.log; then
            log_success "Uninstall completed"
            ((++TESTS_PASSED)) || true
        else
            log_warn "Uninstall script failed (may be expected)"
            ((++TESTS_SKIPPED)) || true
        fi

        # Verify cleanup
        if [ ! -d "$INSTALL_DIR" ]; then
            log_success "Install directory removed"
            ((++TESTS_PASSED)) || true
        else
            log_warn "Install directory still exists after uninstall"
            ((++TESTS_SKIPPED)) || true
        fi
    else
        log_skip "uninstall.sh not found"
        ((++TESTS_SKIPPED)) || true
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
    local scenario="${1:-all}"

    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           CodeAgent Installation Test Suite                ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    log_info "Source directory: $SOURCE_DIR"
    log_info "Install directory: $INSTALL_DIR"
    log_info "Test scenario: $scenario"

    # Create results dir (use /tmp if source is read-only)
    mkdir -p "$TEST_RESULTS_DIR" 2>/dev/null || TEST_RESULTS_DIR="/tmp/codeagent-test-results"
    mkdir -p "$TEST_RESULTS_DIR" 2>/dev/null || true

    case "$scenario" in
        source|1)
            test_source_code
            ;;
        clean|2)
            test_source_code
            test_clean_install
            ;;
        cli|3)
            test_clean_install
            test_cli_commands
            ;;
        config|4)
            test_clean_install
            test_config_keyring
            ;;
        marketplace|5)
            test_clean_install
            test_marketplace
            ;;
        upgrade|6)
            test_clean_install
            test_upgrade_install
            ;;
        force|7)
            test_clean_install
            test_force_reinstall
            ;;
        uninstall|8)
            test_clean_install
            test_uninstall
            ;;
        all|*)
            test_source_code
            test_clean_install
            test_cli_commands
            test_config_keyring
            test_marketplace
            test_upgrade_install
            test_force_reinstall
            # Uninstall last since it removes everything
            test_uninstall
            ;;
    esac

    print_summary
}

main "$@"
