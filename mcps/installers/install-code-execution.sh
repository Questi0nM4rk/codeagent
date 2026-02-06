#!/bin/bash
# ============================================
# CodeAgent Code Execution MCP Installer
# Installs elusznik's code-execution-mode MCP
# ============================================

set -e

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
REGISTRY_FILE="${CODEAGENT_REGISTRY:-$INSTALL_DIR/mcps/mcp-registry.json}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
INSTALLED=0
SKIPPED=0
FAILED=0

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[CODE-EXEC]${NC} $1"; }
log_success() { echo -e "${GREEN}[CODE-EXEC]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[CODE-EXEC]${NC} $1"; }
log_error() { echo -e "${RED}[CODE-EXEC]${NC} $1"; }

# ============================================
# Helper Functions
# ============================================

# Check if MCP is already registered
mcp_exists() {
  local name="$1"
  claude mcp list 2>/dev/null | grep -q "^$name:" 2>/dev/null
}

# Remove MCP registration
remove_mcp() {
  local name="$1"
  claude mcp remove --scope user "$name" 2>/dev/null || true
}

# Check if command exists
command_exists() {
  command -v "$1" &>/dev/null
}

# ============================================
# Prerequisites Check
# ============================================
check_prerequisites() {
  log_info "Checking prerequisites..."

  local missing=()

  # Check Docker
  if ! command_exists docker; then
    missing+=("docker")
  elif ! docker info &>/dev/null; then
    log_warn "Docker is installed but not running"
    missing+=("docker (not running)")
  fi

  # Check uv (for uvx)
  if ! command_exists uv; then
    missing+=("uv")
  fi

  if [ ${#missing[@]} -gt 0 ]; then
    log_error "Missing prerequisites: ${missing[*]}"
    log_error "Install with:"
    log_error "  Docker: pacman -S docker && sudo systemctl start docker"
    log_error "  uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    return 1
  fi

  log_success "All prerequisites met"
  return 0
}

# ============================================
# Docker Image Pull
# ============================================
pull_docker_image() {
  local image="$1"

  log_info "Pulling Docker image: $image"

  # Check if image already exists
  if docker image inspect "$image" &>/dev/null; then
    if [ "$FORCE" != "true" ]; then
      log_info "Image already exists: $image"
      return 0
    fi
    log_info "Force pulling: $image"
  fi

  # Pull image
  if docker pull "$image"; then
    log_success "Pulled: $image"
    return 0
  else
    log_error "Failed to pull: $image"
    return 1
  fi
}

# ============================================
# Install UVX MCPs
# ============================================
install_uvx_mcps() {
  log_info "Installing UVX-based MCPs..."

  # Check if uvx section exists
  if ! jq -e '.uvx' "$REGISTRY_FILE" &>/dev/null; then
    log_info "No UVX MCPs defined in registry"
    return 0
  fi

  local count
  count=$(jq '.uvx | length' "$REGISTRY_FILE")

  for ((i = 0; i < count; i++)); do
    local name
    name=$(jq -r ".uvx[$i].name" "$REGISTRY_FILE")
    local command
    command=$(jq -r ".uvx[$i].command" "$REGISTRY_FILE")
    local args
    args=$(jq -r ".uvx[$i].args | join(\" \")" "$REGISTRY_FILE")
    local docker_image
    docker_image=$(jq -r ".uvx[$i].docker_image // empty" "$REGISTRY_FILE")

    # Pull Docker image if specified
    if [ -n "$docker_image" ]; then
      pull_docker_image "$docker_image" || {
        log_error "Failed to pull required image for $name"
        ((FAILED++)) || true
        continue
      }
    fi

    # Skip if exists and not force
    if [ "$FORCE" != "true" ] && mcp_exists "$name"; then
      log_info "Skipped: $name (already registered)"
      ((SKIPPED++)) || true
      continue
    fi

    # Remove if force
    if [ "$FORCE" = "true" ]; then
      remove_mcp "$name"
    fi

    # Build env args
    local env_args=""
    local env_count
    env_count=$(jq ".uvx[$i].env | length" "$REGISTRY_FILE")
    if [ "$env_count" -gt 0 ]; then
      while IFS= read -r key; do
        local value
        value=$(jq -r ".uvx[$i].env[\"$key\"]" "$REGISTRY_FILE")
        env_args="$env_args -e $key=$value"
      done < <(jq -r ".uvx[$i].env | keys[]" "$REGISTRY_FILE")
    fi

    # Register MCP (user scope for global)
    # Note: name must come before flags for claude mcp add
    log_info "Registering: $name"
    local add_output
    add_output=$(claude mcp add "$name" --scope user $env_args -- $command $args 2>&1) || true

    # Check if registration succeeded
    if mcp_exists "$name"; then
      log_success "Installed: $name"
      ((INSTALLED++)) || true
    else
      log_error "Failed: $name"
      log_error "Output: $add_output"
      ((FAILED++)) || true
    fi
  done
}

# ============================================
# Remove UVX MCPs (for --force)
# ============================================
remove_uvx_mcps() {
  log_warn "Removing CodeAgent UVX MCPs..."

  if ! jq -e '.uvx' "$REGISTRY_FILE" &>/dev/null; then
    return 0
  fi

  local count
  count=$(jq '.uvx | length' "$REGISTRY_FILE")
  for ((i = 0; i < count; i++)); do
    local name
    name=$(jq -r ".uvx[$i].name" "$REGISTRY_FILE")
    if mcp_exists "$name"; then
      remove_mcp "$name"
      log_info "Removed: $name"
    fi
  done
}

# ============================================
# Main
# ============================================
main() {
  # Validate registry
  if [ ! -f "$REGISTRY_FILE" ]; then
    log_error "Registry not found: $REGISTRY_FILE"
    exit 1
  fi

  # Check prerequisites
  check_prerequisites || {
    log_error "Prerequisites check failed"
    exit 1
  }

  # Remove if force
  if [ "$FORCE" = "true" ]; then
    remove_uvx_mcps
  fi

  # Install
  install_uvx_mcps

  # Export counters
  echo "INSTALLED=$INSTALLED"
  echo "SKIPPED=$SKIPPED"
  echo "FAILED=$FAILED"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
