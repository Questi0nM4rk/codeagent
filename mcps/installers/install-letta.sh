#!/bin/bash
# ============================================
# CodeAgent Letta MCP Installer
# Standalone installer for Letta memory system
# ============================================
#
# Letta Architecture:
#   letta/letta:latest image includes built-in PostgreSQL (pgvector)
#   Optionally connects to external Qdrant for vector storage
#
# Components:
#   1. Docker container: letta/letta:latest (port 8283)
#   2. MCP client: npx letta-mcp-server (connects to container)
#
# Environment:
#   OPENAI_API_KEY - Required for embeddings (text-embedding-3-small)
#   LETTA_BASE_URL - Set automatically to http://localhost:8283
#
# References:
#   - https://docs.letta.com/server/docker
#   - https://github.com/oculairmedia/letta-mcp-server

set -e

# ============================================
# Configuration
# ============================================
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
RESET="${CODEAGENT_RESET:-false}"  # Delete data volumes (agents, memories)
ENV_FILE="$INSTALL_DIR/.env"
DOCKER_COMPOSE_FILE="$INSTALL_DIR/infrastructure/docker-compose.yml"

# Letta settings
LETTA_CONTAINER="codeagent-letta"
LETTA_PORT=8283
LETTA_HEALTH_URL="http://localhost:$LETTA_PORT/v1/health/"
LETTA_MCP_NAME="letta"

# Qdrant settings (dependency)
QDRANT_CONTAINER="codeagent-qdrant"
QDRANT_PORT=6333

# Timeouts
HEALTH_TIMEOUT=120
HEALTH_INTERVAL=5

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================
# Logging
# ============================================
log_info() { echo -e "${BLUE}[LETTA]${NC} $1"; }
log_success() { echo -e "${GREEN}[LETTA]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[LETTA]${NC} $1"; }
log_error() { echo -e "${RED}[LETTA]${NC} $1"; }
log_step() { echo -e "${CYAN}[LETTA]${NC} → $1"; }

# ============================================
# Helper Functions
# ============================================

# Check if container is running
container_running() {
    local name="$1"
    docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${name}$"
}

# Check if container exists (running or stopped)
container_exists() {
    local name="$1"
    docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^${name}$"
}

# Get container health status
container_health() {
    local name="$1"
    docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null || echo "unknown"
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

# Wait for service health
wait_for_health() {
    local name="$1"
    local check_type="$2"
    local target="$3"
    local timeout="$4"

    local elapsed=0
    log_info "Waiting for $name to be healthy (timeout: ${timeout}s)..."

    while [ $elapsed -lt $timeout ]; do
        if [ "$check_type" = "http" ]; then
            if health_check_http "$target"; then
                log_success "$name is healthy"
                return 0
            fi
        elif [ "$check_type" = "tcp" ]; then
            if health_check_tcp "$target"; then
                log_success "$name is healthy"
                return 0
            fi
        fi

        sleep $HEALTH_INTERVAL
        elapsed=$((elapsed + HEALTH_INTERVAL))
        echo -n "."
    done

    echo ""
    log_error "$name failed health check after ${timeout}s"
    return 1
}

# Check if MCP is registered
mcp_exists() {
    local name="$1"
    claude mcp list 2>/dev/null | grep -q "^$name:" 2>/dev/null
}

# Remove MCP registration (user scope for global)
remove_mcp() {
    local name="$1"
    claude mcp remove --scope user "$name" 2>/dev/null || true
}

# Get env value from file or environment
get_env_value() {
    local key="$1"

    # Check environment first
    if [ -n "${!key}" ]; then
        echo "${!key}"
        return
    fi

    # Check .env file
    if [ -f "$ENV_FILE" ]; then
        grep "^$key=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | head -1
    fi
}

# ============================================
# Pre-flight Checks
# ============================================
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log_error "Docker not running"
        exit 1
    fi
    log_success "Docker available"

    # Check Claude CLI
    if ! command -v claude &> /dev/null; then
        log_error "Claude Code CLI not found"
        exit 1
    fi
    log_success "Claude CLI available"

    # Check npx
    if ! command -v npx &> /dev/null; then
        log_error "npx not found (required for letta-mcp-server)"
        exit 1
    fi
    log_success "npx available"

    # Check OPENAI_API_KEY
    local openai_key=$(get_env_value "OPENAI_API_KEY")
    if [ -z "$openai_key" ]; then
        log_warn "OPENAI_API_KEY not set - Letta embeddings will fail"
        log_info "Set in $ENV_FILE or environment"
    else
        log_success "OPENAI_API_KEY configured"
    fi
}

# ============================================
# Start Infrastructure
# ============================================
start_infrastructure() {
    log_info "Starting Letta infrastructure..."

    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        log_error "docker-compose.yml not found: $DOCKER_COMPOSE_FILE"
        exit 1
    fi

    local compose_dir=$(dirname "$DOCKER_COMPOSE_FILE")

    # Force mode: stop and remove containers (but preserve volumes unless RESET)
    if [ "$FORCE" = "true" ]; then
        log_warn "Force mode: recreating containers..."

        cd "$compose_dir"
        docker compose stop qdrant letta 2>/dev/null || true
        docker compose rm -f qdrant letta 2>/dev/null || true

        # Only remove volumes if explicitly requested with RESET flag
        # This preserves Letta agents and memories during normal --force
        if [ "$RESET" = "true" ]; then
            log_warn "Reset mode: deleting all Letta data (agents, memories)..."
            docker volume rm codeagent_qdrant_data 2>/dev/null || true
            docker volume rm codeagent_letta_data 2>/dev/null || true
            log_success "Removed Letta data volumes"
        else
            log_info "Preserving Letta data (use --reset to delete)"
        fi

        cd - > /dev/null
        log_success "Removed existing Letta containers"
    fi

    # Start containers
    cd "$compose_dir"

    # Start Qdrant first (Letta dependency)
    log_step "Starting Qdrant..."
    docker compose up -d qdrant

    # Wait for Qdrant
    if ! wait_for_health "Qdrant" "tcp" "$QDRANT_PORT" 60; then
        log_error "Qdrant failed to start"
        docker logs $QDRANT_CONTAINER 2>&1 | tail -20
        exit 1
    fi

    # Start Letta
    log_step "Starting Letta..."
    docker compose up -d letta

    cd - > /dev/null

    # Wait for Letta
    if ! wait_for_health "Letta" "http" "$LETTA_HEALTH_URL" "$HEALTH_TIMEOUT"; then
        log_error "Letta failed to start"
        log_info "Check logs: docker logs $LETTA_CONTAINER"
        docker logs $LETTA_CONTAINER 2>&1 | tail -30
        exit 1
    fi
}

# ============================================
# Register MCP
# ============================================
register_mcp() {
    log_info "Registering Letta MCP..."

    # Remove existing registration if force
    if [ "$FORCE" = "true" ] || mcp_exists "$LETTA_MCP_NAME"; then
        log_step "Removing existing registration..."
        remove_mcp "$LETTA_MCP_NAME"
    fi

    # Register with Claude (user scope for global)
    # Note: LETTA_BASE_URL without /v1 suffix for the MCP server
    log_step "Registering letta-mcp-server..."

    if claude mcp add --scope user "$LETTA_MCP_NAME" \
        --env "LETTA_BASE_URL=http://localhost:$LETTA_PORT" \
        -- npx -y letta-mcp-server 2>/dev/null; then
        log_success "Letta MCP registered"
    else
        log_error "Failed to register Letta MCP"
        exit 1
    fi
}

# ============================================
# Verify Installation
# ============================================
verify_installation() {
    log_info "Verifying installation..."

    local all_ok=true

    # Check Qdrant container
    if container_running "$QDRANT_CONTAINER"; then
        log_success "Qdrant container: running"
    else
        log_error "Qdrant container: not running"
        all_ok=false
    fi

    # Check Letta container
    if container_running "$LETTA_CONTAINER"; then
        local health=$(container_health "$LETTA_CONTAINER")
        if [ "$health" = "healthy" ]; then
            log_success "Letta container: healthy"
        else
            log_warn "Letta container: running (health: $health)"
        fi
    else
        log_error "Letta container: not running"
        all_ok=false
    fi

    # Check Letta health endpoint
    if health_check_http "$LETTA_HEALTH_URL"; then
        log_success "Letta API: responding"

        # Get version info
        local health_response=$(curl -sf "$LETTA_HEALTH_URL" 2>/dev/null)
        if [ -n "$health_response" ]; then
            log_info "Response: $health_response"
        fi
    else
        log_error "Letta API: not responding"
        all_ok=false
    fi

    # Check MCP registration
    if mcp_exists "$LETTA_MCP_NAME"; then
        log_success "MCP registration: OK"
    else
        log_error "MCP registration: not found"
        all_ok=false
    fi

    if [ "$all_ok" = "true" ]; then
        return 0
    else
        return 1
    fi
}

# ============================================
# Show Status
# ============================================
show_status() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                  Letta Installation Complete                   ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}Container:${NC}  $LETTA_CONTAINER"
    echo -e "  ${GREEN}Port:${NC}       $LETTA_PORT"
    echo -e "  ${GREEN}Health:${NC}     $LETTA_HEALTH_URL"
    echo -e "  ${GREEN}MCP:${NC}        $LETTA_MCP_NAME"
    echo ""
    echo -e "  ${YELLOW}Test commands:${NC}"
    echo -e "    curl $LETTA_HEALTH_URL"
    echo -e "    claude mcp list | grep letta"
    echo -e "    docker logs $LETTA_CONTAINER"
    echo ""
}

# ============================================
# Main
# ============================================
main() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                  CodeAgent Letta Installer                     ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ "$FORCE" = "true" ]; then
        log_warn "Force mode: will reinstall Letta from scratch"
    fi

    # Run installation steps
    preflight_checks
    echo ""

    start_infrastructure
    echo ""

    register_mcp
    echo ""

    if verify_installation; then
        show_status
        exit 0
    else
        log_error "Installation verification failed"
        exit 1
    fi
}

# ============================================
# Parse Arguments
# ============================================
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f)
            FORCE=true
            shift
            ;;
        --status|-s)
            # Just show status, don't install
            verify_installation
            exit $?
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --force, -f    Force reinstall (removes existing data)"
            echo "  --status, -s   Check installation status"
            echo "  --help, -h     Show this help"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Run
main "$@"
