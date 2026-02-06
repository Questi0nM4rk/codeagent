#!/bin/bash
# ============================================
# CodeAgent Self-Hosted Services Installer
# Sets up Penpot, Appwrite, and Convex
# ============================================

set -e

# Configuration (inherited from parent)
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
FORCE="${CODEAGENT_FORCE:-false}"
SERVICES_DIR="$INSTALL_DIR/infrastructure/services"

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
log_info() { echo -e "${BLUE}[SELF-HOSTED]${NC} $1"; }
log_success() { echo -e "${GREEN}[SELF-HOSTED]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[SELF-HOSTED]${NC} $1"; }
log_error() { echo -e "${RED}[SELF-HOSTED]${NC} $1"; }

# ============================================
# Check if service is running
# ============================================
service_running() {
  local service="$1"
  docker ps --format '{{.Names}}' 2>/dev/null | grep -q "codeagent-${service}" 2>/dev/null
}

# ============================================
# Ensure network exists
# ============================================
ensure_network() {
  if ! docker network ls --format '{{.Name}}' | grep -q "^codeagent-network$"; then
    log_info "Creating codeagent-network..."
    docker network create codeagent-network
  fi
}

# ============================================
# Pull images for a service
# ============================================
pull_images() {
  local compose_file="$1"
  local service_name="$2"

  log_info "Pulling images for $service_name..."
  if ! docker compose -f "$compose_file" pull --quiet 2>/dev/null; then
    log_error "Failed to pull images for $service_name"
    return 1
  fi
}

# ============================================
# Start a service
# ============================================
start_service() {
  local compose_file="$1"
  local service_name="$2"

  log_info "Starting $service_name..."
  if docker compose -f "$compose_file" up -d 2>/dev/null; then
    log_success "  Started: $service_name"
    return 0
  else
    log_error "  Failed to start: $service_name"
    return 1
  fi
}

# ============================================
# Stop a service
# ============================================
stop_service() {
  local compose_file="$1"
  local service_name="$2"

  log_info "Stopping $service_name..."
  docker compose -f "$compose_file" down 2>/dev/null || true
}

# ============================================
# Install Penpot (pull images only)
# ============================================
install_penpot() {
  local compose_file="$SERVICES_DIR/penpot.yml"

  if [ ! -f "$compose_file" ]; then
    log_warn "Penpot compose file not found: $compose_file"
    ((FAILED++)) || true
    return 1
  fi

  # Pull images (don't start - save RAM)
  pull_images "$compose_file" "Penpot"
  ((INSTALLED++)) || true
  log_success "  Penpot ready"
  log_info "    Start with: codeagent start penpot"
}

# ============================================
# Install Convex (pull images only)
# ============================================
install_convex() {
  local compose_file="$SERVICES_DIR/convex.yml"

  if [ ! -f "$compose_file" ]; then
    log_warn "Convex compose file not found: $compose_file"
    ((FAILED++)) || true
    return 1
  fi

  # Pull images (don't start - save RAM)
  pull_images "$compose_file" "Convex"
  ((INSTALLED++)) || true
  log_success "  Convex ready"
  log_info "    Start with: codeagent start convex"
}

# ============================================
# Install Appwrite (pull images only)
# ============================================
install_appwrite() {
  local compose_file="$SERVICES_DIR/appwrite.yml"

  if [ ! -f "$compose_file" ]; then
    log_warn "Appwrite compose file not found: $compose_file"
    ((FAILED++)) || true
    return 1
  fi

  # Pull images (don't start - save RAM)
  pull_images "$compose_file" "Appwrite"
  ((INSTALLED++)) || true
  log_success "  Appwrite ready"
  log_info "    Start with: codeagent start appwrite"
}

# ============================================
# Remove all self-hosted services
# ============================================
remove_all() {
  log_warn "Removing all self-hosted services..."

  for compose_file in "$SERVICES_DIR"/*.yml; do
    if [ -f "$compose_file" ]; then
      local name
      name=$(basename "$compose_file" .yml)
      docker compose -f "$compose_file" down 2>/dev/null || true
      log_info "  Removed: $name"
    fi
  done
}

# ============================================
# Status check
# ============================================
status_check() {
  echo ""
  log_info "Self-hosted services (images pulled, not started):"
  log_info "  penpot   - Start with: codeagent start penpot"
  log_info "  convex   - Start with: codeagent start convex"
  log_info "  appwrite - Start with: codeagent start appwrite"
  log_info "  (all)    - Start with: codeagent start all"
}

# ============================================
# Main
# ============================================
main() {
  log_info "Pulling self-hosted service images (not starting)..."

  # Check Docker
  if ! command -v docker &>/dev/null; then
    log_error "Docker not found - required for self-hosted services"
    exit 1
  fi

  if ! docker info &>/dev/null; then
    log_error "Docker not running - please start Docker first"
    exit 1
  fi

  # Ensure network exists
  ensure_network

  # Remove if force
  if [ "$FORCE" = "true" ]; then
    remove_all
  fi

  # Install services
  echo ""
  log_info "Installing services..."

  install_penpot
  install_convex
  install_appwrite

  # Status
  status_check

  # Export counters
  echo "INSTALLED=$INSTALLED"
  echo "SKIPPED=$SKIPPED"
  echo "FAILED=$FAILED"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
