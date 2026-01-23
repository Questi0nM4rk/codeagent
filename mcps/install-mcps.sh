#!/bin/bash
# ============================================
# CodeAgent MCP Installation Orchestrator
# Coordinates all MCP sub-installers
# ============================================

set -e

# Configuration
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
RESET="${CODEAGENT_RESET:-false}" # Delete data volumes (agents, memories)
NO_DOCKER="${CODEAGENT_NO_DOCKER:-false}"
REGISTRY_FILE="$INSTALL_DIR/mcps/mcp-registry.json"
INSTALLERS_DIR="$INSTALL_DIR/mcps/installers"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters (aggregated from sub-installers)
TOTAL_INSTALLED=0
TOTAL_SKIPPED=0
TOTAL_FAILED=0

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================
# Parse Arguments
# ============================================
while [[ $# -gt 0 ]]; do
  case $1 in
    --force | -f)
      FORCE=true
      shift
      ;;
    --reset)
      RESET=true
      shift
      ;;
    --no-docker)
      NO_DOCKER=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# ============================================
# Pre-flight Checks
# ============================================
preflight_checks() {
  log_info "Running pre-flight checks..."

  # Check Claude CLI
  if ! command -v claude &>/dev/null; then
    log_error "Claude Code CLI not found"
    log_info "Install from: https://claude.ai/code"
    exit 1
  fi
  log_success "Claude Code CLI found"

  # Check jq for JSON parsing
  if ! command -v jq &>/dev/null; then
    log_error "jq not found - required for JSON parsing"
    log_info "Install with: pacman -S jq (Arch) or apt install jq (Debian)"
    exit 1
  fi

  # Check registry exists
  if [ ! -f "$REGISTRY_FILE" ]; then
    log_error "MCP registry not found: $REGISTRY_FILE"
    exit 1
  fi
  log_success "MCP registry found"

  # Check Docker (unless --no-docker)
  if [ "$NO_DOCKER" != "true" ]; then
    if ! command -v docker &>/dev/null; then
      log_warn "Docker not found - Docker MCPs will be skipped"
      NO_DOCKER=true
    elif ! docker info &>/dev/null; then
      log_warn "Docker not running - Docker MCPs will be skipped"
      NO_DOCKER=true
    else
      log_success "Docker available"
    fi
  fi

  # Check npm/npx (required for NPM MCPs)
  if ! command -v npx &>/dev/null; then
    log_error "npx not found - required for NPM MCPs"
    log_info "Install Node.js from: https://nodejs.org/"
    exit 1
  fi
  log_success "npx available"

  # Check Python
  if ! command -v python3 &>/dev/null; then
    log_warn "Python 3 not found - Python MCPs will be skipped"
  else
    log_success "Python 3 available"
  fi

  # Check uv (for uvx)
  if ! command -v uv &>/dev/null; then
    log_warn "uv not found - Code execution MCP will be skipped"
    log_info "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
  else
    log_success "uv available"
  fi
}

# ============================================
# Run Sub-installer
# ============================================
run_installer() {
  local installer="$1"
  local name="$2"

  if [ ! -f "$installer" ]; then
    log_warn "Installer not found: $installer"
    return 0
  fi

  echo ""
  log_info "Running $name installer..."

  # Export environment for sub-installer
  export CODEAGENT_HOME="$INSTALL_DIR"
  export CODEAGENT_FORCE="$FORCE"
  export CODEAGENT_RESET="$RESET"
  export CODEAGENT_NO_DOCKER="$NO_DOCKER"
  export CODEAGENT_REGISTRY="$REGISTRY_FILE"

  # Run and capture output
  local output
  if output=$(bash "$installer" 2>&1); then
    # Parse counters from output
    local installed
    installed=$(echo "$output" | grep "INSTALLED=" | tail -1 | cut -d= -f2)
    local skipped
    skipped=$(echo "$output" | grep "SKIPPED=" | tail -1 | cut -d= -f2)
    local failed
    failed=$(echo "$output" | grep "FAILED=" | tail -1 | cut -d= -f2)

    # Aggregate
    TOTAL_INSTALLED=$((TOTAL_INSTALLED + ${installed:-0}))
    TOTAL_SKIPPED=$((TOTAL_SKIPPED + ${skipped:-0}))
    TOTAL_FAILED=$((TOTAL_FAILED + ${failed:-0}))

    # Show output (excluding counter lines)
    echo "$output" | grep -v "INSTALLED=\|SKIPPED=\|FAILED=" || true
  else
    log_error "$name installer failed"
    echo "$output" | grep -v "INSTALLED=\|SKIPPED=\|FAILED=" || true
  fi
}

# ============================================
# Remove ALL MCPs (for --force complete wipe)
# ============================================
remove_all_mcps() {
  log_warn "Removing ALL MCPs from system..."

  # Get list of all registered MCPs (format: "name: command - status")
  # Filter lines containing ": " to exclude headers like "Checking MCP server health..."
  local mcp_list
  mcp_list=$(claude mcp list 2>/dev/null | grep ": .* - " | cut -d':' -f1 || echo "")

  if [ -z "$mcp_list" ]; then
    log_info "No MCPs currently registered"
    return 0
  fi

  local removed=0
  while IFS= read -r name; do
    if [ -n "$name" ]; then
      # Remove from all scopes (user and local) for complete wipe
      claude mcp remove --scope user "$name" 2>/dev/null || true
      claude mcp remove --scope local "$name" 2>/dev/null || true
      log_info "  Removed: $name"
      removed=$((removed + 1))
    fi
  done <<<"$mcp_list"

  log_success "Removed $removed MCPs"
}

# ============================================
# Remove All CodeAgent MCPs (for --force)
# ============================================
remove_all_codeagent_mcps() {
  log_warn "Removing all CodeAgent-managed MCPs..."

  # NPM MCPs
  local npm_count
  npm_count=$(jq '.npm | length' "$REGISTRY_FILE")
  for ((i = 0; i < npm_count; i++)); do
    local name
    name=$(jq -r ".npm[$i].name" "$REGISTRY_FILE")
    if claude mcp list 2>/dev/null | grep -q "^$name:"; then
      claude mcp remove "$name" 2>/dev/null || true
      log_info "  Removed: $name"
    fi
  done

  # Optional NPM MCPs
  local npm_opt_count
  npm_opt_count=$(jq '.npm_optional | length' "$REGISTRY_FILE")
  for ((i = 0; i < npm_opt_count; i++)); do
    local name
    name=$(jq -r ".npm_optional[$i].name" "$REGISTRY_FILE")
    if claude mcp list 2>/dev/null | grep -q "^$name:"; then
      claude mcp remove "$name" 2>/dev/null || true
      log_info "  Removed: $name"
    fi
  done

  # Python MCPs
  local python_count
  python_count=$(jq '.python | length' "$REGISTRY_FILE")
  for ((i = 0; i < python_count; i++)); do
    local name
    name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
    if claude mcp list 2>/dev/null | grep -q "^$name:"; then
      claude mcp remove "$name" 2>/dev/null || true
      log_info "  Removed: $name"
    fi
  done

  # Docker MCPs
  local docker_count
  docker_count=$(jq '.docker | length' "$REGISTRY_FILE")
  for ((i = 0; i < docker_count; i++)); do
    local has_mcp
    has_mcp=$(jq -r ".docker[$i].mcp_registration" "$REGISTRY_FILE")
    if [ "$has_mcp" = "true" ]; then
      local name
      name=$(jq -r ".docker[$i].mcp_name" "$REGISTRY_FILE")
      if claude mcp list 2>/dev/null | grep -q "^$name:"; then
        claude mcp remove "$name" 2>/dev/null || true
        log_info "  Removed: $name"
      fi
    fi
  done

  # UVX MCPs (code execution)
  if jq -e '.uvx' "$REGISTRY_FILE" &>/dev/null; then
    local uvx_count
    uvx_count=$(jq '.uvx | length' "$REGISTRY_FILE")
    for ((i = 0; i < uvx_count; i++)); do
      local name
      name=$(jq -r ".uvx[$i].name" "$REGISTRY_FILE")
      if claude mcp list 2>/dev/null | grep -q "^$name:"; then
        claude mcp remove "$name" 2>/dev/null || true
        log_info "  Removed: $name"
      fi
    done
  fi

  log_success "Removed all CodeAgent MCPs"
}

# ============================================
# Verify All MCPs
# ============================================
verify_all_mcps() {
  echo ""
  log_info "Verifying all MCP registrations..."

  local mcp_list
  mcp_list=$(claude mcp list 2>/dev/null || echo "")
  local all_ok=true

  # NPM MCPs
  local npm_count
  npm_count=$(jq '.npm | length' "$REGISTRY_FILE")
  for ((i = 0; i < npm_count; i++)); do
    local name
    name=$(jq -r ".npm[$i].name" "$REGISTRY_FILE")
    if echo "$mcp_list" | grep -q "^$name:"; then
      log_success "  $name"
    else
      log_warn "  $name (not registered)"
      all_ok=false
    fi
  done

  # Python MCPs
  local python_count
  python_count=$(jq '.python | length' "$REGISTRY_FILE")
  for ((i = 0; i < python_count; i++)); do
    local name
    name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
    if echo "$mcp_list" | grep -q "^$name:"; then
      log_success "  $name"
    else
      log_warn "  $name (not registered)"
      all_ok=false
    fi
  done

  # Docker MCPs
  local docker_count
  docker_count=$(jq '.docker | length' "$REGISTRY_FILE")
  for ((i = 0; i < docker_count; i++)); do
    local has_mcp
    has_mcp=$(jq -r ".docker[$i].mcp_registration" "$REGISTRY_FILE")
    if [ "$has_mcp" = "true" ]; then
      local name
      name=$(jq -r ".docker[$i].mcp_name" "$REGISTRY_FILE")
      if echo "$mcp_list" | grep -q "^$name:"; then
        log_success "  $name"
      else
        log_warn "  $name (not registered - run 'codeagent start' first)"
        all_ok=false
      fi
    fi
  done

  # UVX MCPs
  if jq -e '.uvx' "$REGISTRY_FILE" &>/dev/null; then
    local uvx_count
    uvx_count=$(jq '.uvx | length' "$REGISTRY_FILE")
    for ((i = 0; i < uvx_count; i++)); do
      local name
      name=$(jq -r ".uvx[$i].name" "$REGISTRY_FILE")
      if echo "$mcp_list" | grep -q "^$name:"; then
        log_success "  $name"
      else
        log_warn "  $name (not registered)"
        all_ok=false
      fi
    done
  fi

  echo ""
  if [ "$all_ok" = "true" ]; then
    log_success "All MCPs verified"
  else
    log_warn "Some MCPs are not registered"
  fi
}

# ============================================
# Report Summary
# ============================================
report_summary() {
  echo ""
  echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}║                  MCP Installation Summary                      ║${NC}"
  echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  echo -e "  ${GREEN}Installed:${NC} $TOTAL_INSTALLED"
  echo -e "  ${BLUE}Skipped:${NC}   $TOTAL_SKIPPED"
  echo -e "  ${RED}Failed:${NC}    $TOTAL_FAILED"
  echo ""
  echo -e "Run ${YELLOW}claude mcp list${NC} to see all registered MCPs."
  echo ""
}

# ============================================
# Main
# ============================================
main() {
  echo ""
  echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}║                  CodeAgent MCP Installer                       ║${NC}"
  echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
  echo ""

  if [ "$FORCE" = "true" ]; then
    log_warn "Force mode: reinstalling all CodeAgent MCPs"
  fi

  # Pre-flight checks
  preflight_checks

  # Remove ALL MCPs if force (complete clean slate)
  if [ "$FORCE" = "true" ]; then
    echo ""
    remove_all_mcps
  fi

  # Run sub-installers
  run_installer "$INSTALLERS_DIR/install-npm-mcps.sh" "NPM"
  run_installer "$INSTALLERS_DIR/install-python-mcps.sh" "Python"

  if [ "$NO_DOCKER" != "true" ]; then
    run_installer "$INSTALLERS_DIR/install-docker-mcps.sh" "Docker"
  fi

  # Code execution MCP (requires uv + docker available)
  # Note: --no-docker skips infrastructure, but code-execution only needs Docker CLI
  if command -v uv &>/dev/null && command -v docker &>/dev/null && docker info &>/dev/null; then
    run_installer "$INSTALLERS_DIR/install-code-execution.sh" "Code Execution"
  elif command -v uv &>/dev/null; then
    log_warn "Skipping code-execution MCP (Docker not available)"
  fi

  # Verify
  verify_all_mcps

  # Summary
  report_summary

  # Exit with error if any failed
  if [ "$TOTAL_FAILED" -gt 0 ]; then
    exit 1
  fi
}

# Run
main "$@"
