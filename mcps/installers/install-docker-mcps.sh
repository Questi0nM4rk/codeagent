#!/bin/bash
# ============================================
# CodeAgent Docker MCP Installer
# Orchestrates Docker-based services (Qdrant for reflection)
# ============================================
#
# Note: A-MEM uses local file storage, not Docker.
# This installer only handles Qdrant for the reflection MCP.

set -e

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
# shellcheck disable=SC2034  # FORCE available for future use
FORCE="${CODEAGENT_FORCE:-false}"
NO_DOCKER="${CODEAGENT_NO_DOCKER:-false}"
DOCKER_COMPOSE_FILE="$INSTALL_DIR/infrastructure/docker-compose.yml"

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

# Health check - TCP port
health_check_tcp() {
  local port=$1
  timeout 2 bash -c "</dev/tcp/localhost/$port" 2>/dev/null
}

# Wait for Qdrant to be healthy
wait_for_qdrant() {
  local timeout=60
  local elapsed=0
  log_info "Waiting for Qdrant to be healthy (timeout: ${timeout}s)..."

  while [ $elapsed -lt $timeout ]; do
    if health_check_tcp 6333; then
      log_success "Qdrant is healthy"
      return 0
    fi
    sleep 5
    elapsed=$((elapsed + 5))
    echo -n "."
  done

  echo ""
  log_error "Qdrant failed health check after ${timeout}s"
  return 1
}

# ============================================
# Start Qdrant
# ============================================
start_qdrant() {
  if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    log_error "docker-compose.yml not found: $DOCKER_COMPOSE_FILE"
    return 1
  fi

  local compose_dir
  compose_dir=$(dirname "$DOCKER_COMPOSE_FILE")
  cd "$compose_dir"

  log_info "Starting Qdrant..."
  docker compose up -d qdrant

  if wait_for_qdrant; then
    ((DOCKER_INSTALLED++)) || true
    cd - >/dev/null
    return 0
  else
    ((DOCKER_FAILED++)) || true
    cd - >/dev/null
    return 1
  fi
}

# ============================================
# Check Infrastructure Status
# ============================================
check_infrastructure_status() {
  log_info "Checking Docker infrastructure status..."

  local all_ok=true

  # Check Qdrant
  if health_check_tcp 6333; then
    log_success "  qdrant: healthy"
  else
    log_warn "  qdrant: not responding"
    all_ok=false
  fi

  # Check A-MEM storage (local, not Docker)
  if [ -d "$HOME/.codeagent/memory" ]; then
    log_success "  A-MEM storage: ready"
  else
    log_info "  A-MEM storage: will be created on first use"
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
  if ! command -v docker &>/dev/null; then
    log_warn "Docker not found, skipping Docker MCPs"
    echo "DOCKER_INSTALLED=0"
    echo "DOCKER_SKIPPED=0"
    echo "DOCKER_FAILED=0"
    exit 0
  fi

  if ! docker info &>/dev/null; then
    log_warn "Docker not running, skipping Docker MCPs"
    echo "DOCKER_INSTALLED=0"
    echo "DOCKER_SKIPPED=0"
    echo "DOCKER_FAILED=0"
    exit 0
  fi

  log_info "Installing Docker-based MCPs..."

  # Start Qdrant (for reflection MCP)
  start_qdrant

  echo ""
  check_infrastructure_status || true

  # Export counters (without DOCKER_ prefix for parent script)
  echo "INSTALLED=$DOCKER_INSTALLED"
  echo "SKIPPED=$DOCKER_SKIPPED"
  echo "FAILED=$DOCKER_FAILED"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
