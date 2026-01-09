#!/bin/bash
# ============================================
# CodeAgent Quick Test (Host-based, no Docker)
# Validates source code without full installation
# Usage: ./test-quick.sh
# ============================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="${SCRIPT_DIR}/../.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
SKIPPED=0

log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((++PASSED)) || true; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; ((++FAILED)) || true; }
log_skip() { echo -e "${YELLOW}[SKIP]${NC} $1"; ((++SKIPPED)) || true; }
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         CodeAgent Quick Validation (Host-based)           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# 1. Check required files exist
# ============================================
log_info "Checking required files..."

for file in install.sh uninstall.sh; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        log_pass "$file exists"
    else
        log_fail "$file missing"
    fi
done

# ============================================
# 2. Check bin scripts
# ============================================
log_info "Checking bin scripts..."

for script in codeagent codeagent-start codeagent-stop codeagent-status codeagent-config codeagent-marketplace; do
    if [ -f "$SOURCE_DIR/bin/$script" ]; then
        if [ -x "$SOURCE_DIR/bin/$script" ]; then
            log_pass "bin/$script (executable)"
        else
            log_fail "bin/$script (not executable)"
        fi
    else
        log_fail "bin/$script missing"
    fi
done

# ============================================
# 3. Shellcheck validation
# ============================================
if command -v shellcheck &>/dev/null; then
    log_info "Running shellcheck..."

    # Main scripts
    for script in "$SOURCE_DIR/install.sh" "$SOURCE_DIR/uninstall.sh"; do
        if [ -f "$script" ]; then
            # Exclude style/info warnings, only fail on actual errors
            if shellcheck -e SC2034,SC2155,SC2086,SC1090,SC2015,SC2129,SC2016,SC2012,SC2164 -S warning "$script" 2>/dev/null; then
                log_pass "shellcheck: $(basename "$script")"
            else
                log_fail "shellcheck: $(basename "$script")"
            fi
        fi
    done

    # Bin scripts
    for script in "$SOURCE_DIR"/bin/*; do
        if [ -f "$script" ]; then
            # Exclude style/info warnings, only fail on actual errors
            # SC2034: unused variables (common for colors)
            # SC2155: declare and assign separately (style)
            # SC2086: double quote variables (info)
            # SC1090: can't follow dynamic source (info)
            if shellcheck -e SC2034,SC2155,SC2086,SC1090 -S warning "$script" 2>/dev/null; then
                log_pass "shellcheck: bin/$(basename "$script")"
            else
                log_fail "shellcheck: bin/$(basename "$script")"
            fi
        fi
    done
else
    log_skip "shellcheck not installed"
fi

# ============================================
# 4. Check skills
# ============================================
log_info "Checking skills..."

skill_count=$(find "$SOURCE_DIR/framework/skills" -name "SKILL.md" 2>/dev/null | wc -l)
if [ "$skill_count" -ge 15 ]; then
    log_pass "Skills: $skill_count found"
else
    log_fail "Skills: expected 15+, found $skill_count"
fi

# Check specific new skills
for skill in systematic-debugging brainstorming skill-creator; do
    if [ -f "$SOURCE_DIR/framework/skills/$skill/SKILL.md" ]; then
        log_pass "Skill: $skill"
    else
        log_fail "Skill: $skill missing"
    fi
done

# ============================================
# 5. Check commands
# ============================================
log_info "Checking commands..."

cmd_count=$(find "$SOURCE_DIR/framework/commands" -name "*.md" 2>/dev/null | wc -l)
if [ "$cmd_count" -ge 5 ]; then
    log_pass "Commands: $cmd_count found"
else
    log_fail "Commands: expected 5+, found $cmd_count"
fi

# ============================================
# 5b. Check agents
# ============================================
log_info "Checking agents..."

agent_count=$(find "$SOURCE_DIR/framework/agents" -name "*.md" 2>/dev/null | wc -l)
if [ "$agent_count" -ge 6 ]; then
    log_pass "Agents: $agent_count found"
else
    log_fail "Agents: expected 6+, found $agent_count"
fi

# Check specific core agents
for agent in researcher architect orchestrator implementer reviewer learner; do
    if [ -f "$SOURCE_DIR/framework/agents/$agent.md" ]; then
        log_pass "Agent: $agent"
    else
        log_fail "Agent: $agent missing"
    fi
done

# ============================================
# 6. Check key features in scripts
# ============================================
log_info "Checking script features..."

# codeagent-marketplace should use smithery
if grep -q "@smithery/cli" "$SOURCE_DIR/bin/codeagent-marketplace" 2>/dev/null; then
    log_pass "codeagent-marketplace uses @smithery/cli"
else
    log_fail "codeagent-marketplace missing @smithery/cli"
fi

# codeagent-config should have keyring helpers
if grep -q "store_secret" "$SOURCE_DIR/bin/codeagent-config" 2>/dev/null; then
    log_pass "codeagent-config has store_secret"
else
    log_fail "codeagent-config missing store_secret"
fi

if grep -q "get_secret" "$SOURCE_DIR/bin/codeagent-config" 2>/dev/null; then
    log_pass "codeagent-config has get_secret"
else
    log_fail "codeagent-config missing get_secret"
fi

# codeagent should have marketplace subcommand
if grep -q "marketplace)" "$SOURCE_DIR/bin/codeagent" 2>/dev/null; then
    log_pass "codeagent has marketplace subcommand"
else
    log_fail "codeagent missing marketplace subcommand"
fi

# ============================================
# 7. Check skill format (Iron Laws)
# ============================================
log_info "Checking skill format..."

skills_with_iron_law=0
for skill_file in "$SOURCE_DIR"/framework/skills/*/SKILL.md; do
    if grep -q "Iron Law" "$skill_file" 2>/dev/null; then
        ((++skills_with_iron_law)) || true
    fi
done

if [ "$skills_with_iron_law" -ge 10 ]; then
    log_pass "Skills with Iron Law format: $skills_with_iron_law"
else
    log_fail "Skills with Iron Law format: expected 10+, found $skills_with_iron_law"
fi

# ============================================
# Summary
# ============================================
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Summary${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Passed:${NC}  $PASSED"
echo -e "  ${RED}Failed:${NC}  $FAILED"
echo -e "  ${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed.${NC}"
    exit 1
fi
