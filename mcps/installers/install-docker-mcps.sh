#!/bin/bash
# ============================================
# CodeAgent Docker MCP Installer
# Orchestrates Docker-based services and MCPs
# ============================================
#
# This installer delegates to specialized installers:
#   - install-letta.sh: Handles Letta + Qdrant infrastructure
#
# Other Docker services (neo4j) are infrastructure-only
# and don't require MCP registration.

set -e

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
RESET="${CODEAGENT_RESET:-false}"  # Delete data volumes (agents, memories)
NO_DOCKER="${CODEAGENT_NO_DOCKER:-false}"
REGISTRY_FILE="${CODEAGENT_REGISTRY:-$INSTALL_DIR/mcps/mcp-registry.json}"
DOCKER_COMPOSE_FILE="$INSTALL_DIR/infrastructure/docker-compose.yml"
# Installers directory - use script's location first, then fall back to install dir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLERS_DIR="$SCRIPT_DIR"
# Fall back to install dir if script dir doesn't have the installer
if [ ! -f "$INSTALLERS_DIR/install-letta.sh" ]; then
    INSTALLERS_DIR="$INSTALL_DIR/mcps/installers"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
DOCKER_INSTALLED=0
DOCKER_SKIPPED=0
DOCKER_FAILED=0

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[DOCKER]${NC} $1"; }
log_success() { echo -e "${GREEN}[DOCKER]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[DOCKER]${NC} $1"; }
log_error() { echo -e "${RED}[DOCKER]${NC} $1"; }

# ============================================
# Helper Functions
# ============================================

# Check if MCP is already registered
mcp_exists() {
    local name="$1"
    claude mcp list 2>/dev/null | grep -q "^$name:" 2>/dev/null
}

# Health check - TCP port
health_check_tcp() {
    local port=$1
    timeout 2 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
}

# Health check - HTTP endpoint
health_check_http() {
    local url=$1
    curl -sf --max-time 5 "$url" > /dev/null 2>&1
}

# ============================================
# Start Neo4j (Infrastructure Only)
# ============================================
start_neo4j() {
    log_info "Starting Neo4j..."

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "docker-compose.yml not found: $DOCKER_COMPOSE_FILE"
        return 1
    fi

    local compose_dir=$(dirname "$DOCKER_COMPOSE_FILE")
    cd "$compose_dir"

    # Start Neo4j
    docker compose up -d neo4j

    cd - > /dev/null

    # Wait for health
    log_info "Waiting for Neo4j..."
    local attempts=0
    local max_attempts=30

    while [ $attempts -lt $max_attempts ]; do
        if health_check_http "http://localhost:7474"; then
            log_success "Neo4j is healthy"
            return 0
        fi
        ((attempts++)) || true
        sleep 2
    done

    log_warn "Neo4j health check timed out"
    return 1
}

# ============================================
# Install Letta (Delegated)
# ============================================
install_letta() {
    local letta_installer="$INSTALLERS_DIR/install-letta.sh"

    if [ ! -f "$letta_installer" ]; then
        log_error "Letta installer not found: $letta_installer"
        ((DOCKER_FAILED++)) || true
        return 1
    fi

    log_info "Delegating to Letta installer..."

    # Export environment for sub-installer
    export CODEAGENT_HOME="$INSTALL_DIR"
    export CODEAGENT_FORCE="$FORCE"
    export CODEAGENT_RESET="$RESET"

    # Run Letta installer
    if bash "$letta_installer"; then
        ((DOCKER_INSTALLED++)) || true
        return 0
    else
        ((DOCKER_FAILED++)) || true
        return 1
    fi
}

# ============================================
# Check Infrastructure Status
# ============================================
check_infrastructure_status() {
    log_info "Checking Docker infrastructure status..."

    local all_ok=true

    # Check Neo4j
    if health_check_http "http://localhost:7474"; then
        log_success "  neo4j: healthy"
    else
        log_warn "  neo4j: not responding"
        all_ok=false
    fi

    # Check Qdrant
    if health_check_tcp 6333; then
        log_success "  qdrant: healthy"
    else
        log_warn "  qdrant: not responding"
        all_ok=false
    fi

    # Check Letta
    if health_check_http "http://localhost:8283/v1/health/"; then
        log_success "  letta: healthy"
    else
        log_warn "  letta: not responding"
        all_ok=false
    fi

    # Check Letta MCP
    if mcp_exists "letta"; then
        log_success "  letta MCP: registered"
    else
        log_warn "  letta MCP: not registered"
        all_ok=false
    fi

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
    # Check if Docker is disabled
    if [ "$NO_DOCKER" = "true" ]; then
        log_warn "Docker disabled, skipping Docker MCPs"
        echo "DOCKER_INSTALLED=0"
        echo "DOCKER_SKIPPED=0"
        echo "DOCKER_FAILED=0"
        exit 0
    fi

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_warn "Docker not found, skipping Docker MCPs"
        echo "DOCKER_INSTALLED=0"
        echo "DOCKER_SKIPPED=0"
        echo "DOCKER_FAILED=0"
        exit 0
    fi

    if ! docker info &> /dev/null; then
        log_warn "Docker not running, skipping Docker MCPs"
        echo "DOCKER_INSTALLED=0"
        echo "DOCKER_SKIPPED=0"
        echo "DOCKER_FAILED=0"
        exit 0
    fi

    log_info "Installing Docker-based MCPs..."

    # Start Neo4j (infrastructure only, no MCP)
    start_neo4j || true

    # Install Letta (handles Qdrant dependency + MCP registration)
    install_letta

    echo ""
    check_infrastructure_status || true

    # Export counters
    echo "DOCKER_INSTALLED=$DOCKER_INSTALLED"
    echo "DOCKER_SKIPPED=$DOCKER_SKIPPED"
    echo "DOCKER_FAILED=$DOCKER_FAILED"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
