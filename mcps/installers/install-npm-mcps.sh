#!/bin/bash
# ============================================
# CodeAgent NPM MCP Installer
# Simple one-liner MCPs via npx/uvx
# ============================================

set -e

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
REGISTRY_FILE="${CODEAGENT_REGISTRY:-$INSTALL_DIR/mcps/mcp-registry.json}"
ENV_FILE="$INSTALL_DIR/.env"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters (exported back to parent - must match parent's grep pattern)
INSTALLED=0
SKIPPED=0
FAILED=0

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[NPM]${NC} $1"; }
log_success() { echo -e "${GREEN}[NPM]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[NPM]${NC} $1"; }
log_error() { echo -e "${RED}[NPM]${NC} $1"; }

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

# Get API key value from environment or .env file
get_key_value() {
    local key_name="$1"

    # First check environment
    if [ -n "${!key_name}" ]; then
        echo "${!key_name}"
        return
    fi

    # Fall back to .env file
    if [ -f "$ENV_FILE" ]; then
        local value=$(grep "^$key_name=" "$ENV_FILE" 2>/dev/null | cut -d= -f2-)
        if [ -n "$value" ]; then
            echo "$value"
        fi
    fi
}

# ============================================
# Install Required NPM MCPs
# ============================================
install_npm_required() {
    log_info "Installing required NPM MCPs..."

    local count=$(jq '.npm | length' "$REGISTRY_FILE")

    for ((i=0; i<count; i++)); do
        local name=$(jq -r ".npm[$i].name" "$REGISTRY_FILE")
        local command=$(jq -r ".npm[$i].command" "$REGISTRY_FILE")
        local args=$(jq -r ".npm[$i].args | join(\" \")" "$REGISTRY_FILE")

        # Skip if exists and not force
        if [ "$FORCE" != "true" ] && mcp_exists "$name"; then
            log_info "  Skipped: $name (already registered)"
            ((SKIPPED++)) || true
            continue
        fi

        # Remove if force
        if [ "$FORCE" = "true" ]; then
            remove_mcp "$name"
        fi

        # Register MCP (user scope for global)
        local add_output
        add_output=$(claude mcp add --scope user "$name" -- $command $args 2>&1) || true

        # Check if registration succeeded (either added or already exists)
        if mcp_exists "$name"; then
            log_success "  Installed: $name"
            ((INSTALLED++)) || true
        else
            log_error "  Failed: $name"
            ((FAILED++)) || true
        fi
    done
}

# ============================================
# Install Optional NPM MCPs (require API keys)
# ============================================
install_npm_optional() {
    log_info "Installing optional NPM MCPs..."

    local count=$(jq '.npm_optional | length' "$REGISTRY_FILE")

    for ((i=0; i<count; i++)); do
        local name=$(jq -r ".npm_optional[$i].name" "$REGISTRY_FILE")
        local command=$(jq -r ".npm_optional[$i].command" "$REGISTRY_FILE")
        local args=$(jq -r ".npm_optional[$i].args | join(\" \")" "$REGISTRY_FILE")
        local env_key=$(jq -r ".npm_optional[$i].env_key" "$REGISTRY_FILE")
        local env_var=$(jq -r ".npm_optional[$i].env_var" "$REGISTRY_FILE")

        # Check if API key is available
        local key_value=$(get_key_value "$env_key")
        if [ -z "$key_value" ]; then
            log_info "  Skipped: $name ($env_key not configured)"
            ((SKIPPED++)) || true
            continue
        fi

        # Skip if exists and not force
        if [ "$FORCE" != "true" ] && mcp_exists "$name"; then
            log_info "  Skipped: $name (already registered)"
            ((SKIPPED++)) || true
            continue
        fi

        # Remove if force
        if [ "$FORCE" = "true" ]; then
            remove_mcp "$name"
        fi

        # Register MCP with env var (user scope for global)
        local add_output
        add_output=$(claude mcp add --scope user "$name" --env "$env_var=$key_value" -- $command $args 2>&1) || true

        # Check if registration succeeded (either added or already exists)
        if mcp_exists "$name"; then
            log_success "  Installed: $name"
            ((INSTALLED++)) || true
        else
            log_error "  Failed: $name"
            ((FAILED++)) || true
        fi
    done
}

# ============================================
# Remove NPM MCPs (for --force)
# ============================================
remove_npm_mcps() {
    log_warn "Removing CodeAgent NPM MCPs..."

    # Required MCPs
    local npm_count=$(jq '.npm | length' "$REGISTRY_FILE")
    for ((i=0; i<npm_count; i++)); do
        local name=$(jq -r ".npm[$i].name" "$REGISTRY_FILE")
        if mcp_exists "$name"; then
            remove_mcp "$name"
            log_info "  Removed: $name"
        fi
    done

    # Optional MCPs
    local npm_opt_count=$(jq '.npm_optional | length' "$REGISTRY_FILE")
    for ((i=0; i<npm_opt_count; i++)); do
        local name=$(jq -r ".npm_optional[$i].name" "$REGISTRY_FILE")
        if mcp_exists "$name"; then
            remove_mcp "$name"
            log_info "  Removed: $name"
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

    # Remove if force
    if [ "$FORCE" = "true" ]; then
        remove_npm_mcps
    fi

    # Install
    install_npm_required
    install_npm_optional

    # Export counters (names must match parent's grep pattern)
    echo "INSTALLED=$INSTALLED"
    echo "SKIPPED=$SKIPPED"
    echo "FAILED=$FAILED"
}

# Run if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
