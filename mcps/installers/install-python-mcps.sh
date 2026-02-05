#!/bin/bash
# ============================================
# CodeAgent Python MCP Installer
# Installs from GitHub by default, local path with --local flag
# ============================================

set -euo pipefail

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
LOCAL="${CODEAGENT_LOCAL:-false}"
REGISTRY_FILE="${CODEAGENT_REGISTRY:-$INSTALL_DIR/mcps/mcp-registry.json}"
VENV_DIR="$INSTALL_DIR/venv"
VENV_PIP="$VENV_DIR/bin/pip"
VENV_PYTHON="$VENV_DIR/bin/python"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters (names must match parent's grep pattern)
INSTALLED=0
SKIPPED=0
FAILED=0

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[PYTHON]${NC} $1"; }
log_success() { echo -e "${GREEN}[PYTHON]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[PYTHON]${NC} $1"; }
log_error() { echo -e "${RED}[PYTHON]${NC} $1"; }

# ============================================
# Helper Functions
# ============================================

# Check if MCP is already registered
mcp_exists() {
  local name="$1"
  claude mcp list 2>/dev/null | grep -q "^$name:" 2>/dev/null
}

# Remove MCP registration (user scope for global)
remove_mcp() {
  local name="$1"
  claude mcp remove --scope user "$name" 2>/dev/null || true
}

# Expand tilde in path
expand_path() {
  local path="$1"
  echo "${path/#\~/$HOME}"
}

# ============================================
# Setup Python Virtual Environment
# ============================================
setup_venv() {
  if [[ ! -f "$VENV_PYTHON" ]]; then
    log_info "Creating Python virtual environment..."
    if ! python3 -m venv "$VENV_DIR"; then
      log_error "Failed to create virtual environment"
      log_info "Check python3-venv is installed: apt install python3-venv (Debian) or pacman -S python (Arch)"
      exit 1
    fi
    if ! "$VENV_PIP" install --upgrade pip --quiet; then
      log_error "Failed to upgrade pip in venv"
      exit 1
    fi
  fi

  # Install MCP SDK if not present
  if ! "$VENV_PYTHON" -c "import mcp" 2>/dev/null; then
    log_info "Installing MCP SDK..."
    if ! "$VENV_PIP" install mcp --quiet; then
      log_error "Failed to install MCP SDK"
      exit 1
    fi
  fi
}

# ============================================
# Install Python MCP Package
# ============================================
install_from_github() {
  local name="$1"
  local github="$2"
  local branch="$3"
  local extras="$4"

  local github_url="git+https://github.com/${github}.git"
  if [[ -n "$branch" ]]; then
    github_url="${github_url}@${branch}"
  fi

  # Add extras if specified
  local install_target="$github_url"
  if [[ -n "$extras" ]]; then
    install_target="${github_url}#egg=${name}[${extras}]"
  fi

  log_info "  Installing from GitHub: $github"
  if [[ "$FORCE" == "true" ]]; then
    "$VENV_PIP" install "$install_target" --force-reinstall --quiet 2>&1 || return 1
  else
    "$VENV_PIP" install "$install_target" --quiet 2>&1 || return 1
  fi
  return 0
}

install_from_local() {
  local name="$1"
  local local_path="$2"
  local extras="$3"

  local expanded_path
  expanded_path=$(expand_path "$local_path")

  # Check path exists
  if [[ ! -d "$expanded_path" ]]; then
    log_error "  Local path not found: $expanded_path"
    return 1
  fi

  # Check pyproject.toml exists
  if [[ ! -f "$expanded_path/pyproject.toml" ]]; then
    log_error "  No pyproject.toml found: $expanded_path"
    return 1
  fi

  # Build install target (with optional extras)
  local install_target="$expanded_path"
  if [[ -n "$extras" ]]; then
    install_target="${expanded_path}[${extras}]"
  fi

  log_info "  Installing from local (editable): $expanded_path"
  if [[ "$FORCE" == "true" ]]; then
    "$VENV_PIP" install -e "$install_target" --force-reinstall --quiet 2>&1 || return 1
  else
    "$VENV_PIP" install -e "$install_target" --quiet 2>&1 || return 1
  fi
  return 0
}

# ============================================
# Install Python MCPs
# ============================================
install_python_mcps() {
  if [[ "$LOCAL" == "true" ]]; then
    log_info "Installing Python MCPs (LOCAL/EDITABLE mode)..."
  else
    log_info "Installing Python MCPs (from GitHub)..."
  fi

  local count
  count=$(jq '.python | length' "$REGISTRY_FILE")

  for ((i = 0; i < count; i++)); do
    local name github branch extras local_path module required
    name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
    module=$(jq -r ".python[$i].module" "$REGISTRY_FILE")
    github=$(jq -r ".python[$i].github // empty" "$REGISTRY_FILE")
    branch=$(jq -r ".python[$i].branch // \"main\"" "$REGISTRY_FILE")
    extras=$(jq -r ".python[$i].extras // empty" "$REGISTRY_FILE")
    local_path=$(jq -r ".python[$i].local_path // empty" "$REGISTRY_FILE")
    required=$(jq -r ".python[$i].required // false" "$REGISTRY_FILE")

    # Skip if exists and not force
    if [[ "$FORCE" != "true" ]] && mcp_exists "$name"; then
      log_info "  Skipped: $name (already registered)"
      ((SKIPPED++)) || true
      continue
    fi

    # Install package
    local install_ok=false
    if [[ "$LOCAL" == "true" ]]; then
      # Local mode: install from local path
      if [[ -n "$local_path" ]]; then
        if install_from_local "$name" "$local_path" "$extras"; then
          install_ok=true
        fi
      else
        log_warn "  No local_path defined for $name, falling back to GitHub"
        if [[ -n "$github" ]] && install_from_github "$name" "$github" "$branch" "$extras"; then
          install_ok=true
        fi
      fi
    else
      # GitHub mode (default): install from GitHub
      if [[ -n "$github" ]]; then
        if install_from_github "$name" "$github" "$branch" "$extras"; then
          install_ok=true
        fi
      elif [[ -n "$local_path" ]]; then
        log_warn "  No github defined for $name, falling back to local path"
        if install_from_local "$name" "$local_path" "$extras"; then
          install_ok=true
        fi
      fi
    fi

    if [[ "$install_ok" != "true" ]]; then
      if [[ "$required" == "true" ]]; then
        log_error "  Failed to install required package: $name"
        ((FAILED++)) || true
      else
        log_warn "  Failed to install optional package: $name (skipping)"
        ((SKIPPED++)) || true
      fi
      continue
    fi

    # Remove if force (after package install succeeds)
    if [[ "$FORCE" == "true" ]]; then
      remove_mcp "$name"
    fi

    # Build registration command with env vars if specified
    local env_json
    env_json=$(jq -r ".python[$i].env // {}" "$REGISTRY_FILE")

    # Register MCP with Claude (user scope for global)
    if [[ "$env_json" != "{}" && "$env_json" != "null" ]]; then
      # Has env vars - build --env flags
      local env_flags=""
      while IFS='=' read -r key value; do
        # Expand ${VAR} references
        value=$(eval echo "$value")
        env_flags="$env_flags -e $key=$value"
      done < <(echo "$env_json" | jq -r 'to_entries[] | "\(.key)=\(.value)"')

      # shellcheck disable=SC2086
      if claude mcp add --scope user $env_flags "$name" -- "$VENV_PYTHON" -m "$module" 2>/dev/null; then
        log_success "  Installed: $name (with env)"
        ((INSTALLED++)) || true
      else
        log_error "  Failed to register: $name"
        ((FAILED++)) || true
      fi
    else
      # No env vars
      if claude mcp add --scope user "$name" -- "$VENV_PYTHON" -m "$module" 2>/dev/null; then
        log_success "  Installed: $name"
        ((INSTALLED++)) || true
      else
        log_error "  Failed to register: $name"
        ((FAILED++)) || true
      fi
    fi
  done
}

# ============================================
# Remove Python MCPs
# ============================================
remove_python_mcps() {
  log_warn "Removing CodeAgent Python MCPs..."

  local count
  count=$(jq '.python | length' "$REGISTRY_FILE")

  for ((i = 0; i < count; i++)); do
    local name
    name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
    if mcp_exists "$name"; then
      remove_mcp "$name"
      log_info "  Removed: $name"
    fi
  done
}

# ============================================
# Verify Python MCPs
# ============================================
verify_python_mcps() {
  log_info "Verifying Python MCPs..."

  local count
  count=$(jq '.python | length' "$REGISTRY_FILE")
  local all_ok=true

  for ((i = 0; i < count; i++)); do
    local name module
    name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
    module=$(jq -r ".python[$i].module" "$REGISTRY_FILE")

    # Check if module can be imported
    if "$VENV_PYTHON" -c "import ${module%.*}" 2>/dev/null; then
      if mcp_exists "$name"; then
        log_success "  $name: OK"
      else
        log_warn "  $name: package OK, not registered"
        all_ok=false
      fi
    else
      log_error "  $name: import failed"
      all_ok=false
    fi
  done

  if [[ "$all_ok" == "true" ]]; then
    return 0
  else
    return 1
  fi
}

# ============================================
# Main
# ============================================
main() {
  # Validate registry
  if [[ ! -f "$REGISTRY_FILE" ]]; then
    log_error "Registry not found: $REGISTRY_FILE"
    exit 1
  fi

  # Check Python
  if ! command -v python3 &>/dev/null; then
    log_error "Python 3 not found"
    exit 1
  fi

  # Setup venv
  setup_venv

  # Remove if force
  if [[ "$FORCE" == "true" ]]; then
    remove_python_mcps
  fi

  # Install
  install_python_mcps

  # Verify (optional)
  verify_python_mcps || true

  # Export counters (names must match parent's grep pattern)
  echo "INSTALLED=$INSTALLED"
  echo "SKIPPED=$SKIPPED"
  echo "FAILED=$FAILED"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
