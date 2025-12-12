#!/bin/bash
# ============================================
# CodeAgent Python MCP Installer
# Custom Python MCPs using venv
# ============================================

set -e

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
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

# Counters
PYTHON_INSTALLED=0
PYTHON_SKIPPED=0
PYTHON_FAILED=0

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

# Remove MCP registration
remove_mcp() {
    local name="$1"
    claude mcp remove "$name" 2>/dev/null || true
}

# ============================================
# Setup Python Virtual Environment
# ============================================
setup_venv() {
    if [ ! -f "$VENV_PYTHON" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv "$VENV_DIR"
        "$VENV_PIP" install --upgrade pip --quiet
    fi

    # Install MCP SDK if not present
    if ! "$VENV_PYTHON" -c "import mcp" 2>/dev/null; then
        log_info "Installing MCP SDK..."
        "$VENV_PIP" install mcp --quiet
    fi
}

# ============================================
# Install Python MCP Package
# ============================================
install_python_package() {
    local name="$1"
    local mcp_path="$2"

    # Check pyproject.toml exists
    if [ ! -f "$mcp_path/pyproject.toml" ]; then
        log_error "  No pyproject.toml found: $mcp_path"
        return 1
    fi

    # Install in editable mode
    if [ "$FORCE" = "true" ]; then
        "$VENV_PIP" install -e "$mcp_path" --force-reinstall --quiet 2>/dev/null
    else
        "$VENV_PIP" install -e "$mcp_path" --quiet 2>/dev/null
    fi
}

# ============================================
# Install Python MCPs
# ============================================
install_python_mcps() {
    log_info "Installing Python MCPs..."

    local count=$(jq '.python | length' "$REGISTRY_FILE")

    for ((i=0; i<count; i++)); do
        local name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
        local module=$(jq -r ".python[$i].module" "$REGISTRY_FILE")
        local path=$(jq -r ".python[$i].path" "$REGISTRY_FILE")
        local mcp_path="$INSTALL_DIR/$path"

        # Check MCP directory exists
        if [ ! -d "$mcp_path" ]; then
            log_warn "  Skipped: $name (directory not found: $mcp_path)"
            ((PYTHON_SKIPPED++)) || true
            continue
        fi

        # Skip if exists and not force
        if [ "$FORCE" != "true" ] && mcp_exists "$name"; then
            log_info "  Skipped: $name (already registered)"
            ((PYTHON_SKIPPED++)) || true
            continue
        fi

        # Install package
        if ! install_python_package "$name" "$mcp_path"; then
            log_error "  Failed to install package: $name"
            ((PYTHON_FAILED++)) || true
            continue
        fi

        # Remove if force (after package install succeeds)
        if [ "$FORCE" = "true" ]; then
            remove_mcp "$name"
        fi

        # Register MCP with Claude
        if claude mcp add "$name" -- "$VENV_PYTHON" -m "$module" 2>/dev/null; then
            log_success "  Installed: $name"
            ((PYTHON_INSTALLED++)) || true
        else
            log_error "  Failed to register: $name"
            ((PYTHON_FAILED++)) || true
        fi
    done
}

# ============================================
# Remove Python MCPs
# ============================================
remove_python_mcps() {
    log_warn "Removing CodeAgent Python MCPs..."

    local count=$(jq '.python | length' "$REGISTRY_FILE")

    for ((i=0; i<count; i++)); do
        local name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
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

    local count=$(jq '.python | length' "$REGISTRY_FILE")
    local all_ok=true

    for ((i=0; i<count; i++)); do
        local name=$(jq -r ".python[$i].name" "$REGISTRY_FILE")
        local module=$(jq -r ".python[$i].module" "$REGISTRY_FILE")

        # Check if module can be imported
        if "$VENV_PYTHON" -c "import $module" 2>/dev/null; then
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

    if [ "$all_ok" = "true" ]; then
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
    if [ ! -f "$REGISTRY_FILE" ]; then
        log_error "Registry not found: $REGISTRY_FILE"
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found"
        exit 1
    fi

    # Setup venv
    setup_venv

    # Remove if force
    if [ "$FORCE" = "true" ]; then
        remove_python_mcps
    fi

    # Install
    install_python_mcps

    # Verify (optional)
    verify_python_mcps || true

    # Export counters
    echo "PYTHON_INSTALLED=$PYTHON_INSTALLED"
    echo "PYTHON_SKIPPED=$PYTHON_SKIPPED"
    echo "PYTHON_FAILED=$PYTHON_FAILED"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
