#!/bin/bash
# ============================================
# Full Appwrite BaaS Installation
# Runs the official Appwrite installer for production-ready setup
# ============================================
#
# This script runs Appwrite's official interactive installer which sets up
# ~25 services including workers, schedulers, and function runtimes.
#
# Use this when you need:
# - Serverless functions
# - Background workers (emails, webhooks, etc.)
# - Full production BaaS capabilities
#
# For basic API testing, use the minimal setup via `codeagent start`
#
# Official docs: https://appwrite.io/docs/advanced/self-hosting/installation

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
APPWRITE_VERSION="${APPWRITE_VERSION:-1.8.1}"
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}/services/appwrite-full"

log_info() { echo -e "${BLUE}[APPWRITE]${NC} $1"; }
log_success() { echo -e "${GREEN}[APPWRITE]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[APPWRITE]${NC} $1"; }
log_error() { echo -e "${RED}[APPWRITE]${NC} $1"; }

# ============================================
# Pre-flight checks
# ============================================
preflight() {
  log_info "Checking requirements..."

  # Docker
  if ! command -v docker &>/dev/null; then
    log_error "Docker not found. Please install Docker first."
    exit 1
  fi

  if ! docker info &>/dev/null; then
    log_error "Docker daemon not running. Please start Docker."
    exit 1
  fi

  # Check Docker socket access
  if [ ! -S /var/run/docker.sock ]; then
    log_error "Docker socket not found at /var/run/docker.sock"
    exit 1
  fi

  # Check for port conflicts (Appwrite uses 80/443 by default)
  if ss -tuln 2>/dev/null | grep -q ':80 ' || netstat -tuln 2>/dev/null | grep -q ':80 '; then
    log_warn "Port 80 is in use. The installer will ask for an alternative port."
  fi

  log_success "Requirements satisfied"
}

# ============================================
# Main installation
# ============================================
install_appwrite() {
  log_info "Installing Appwrite ${APPWRITE_VERSION}..."
  echo ""
  echo -e "${CYAN}This will run the official Appwrite interactive installer.${NC}"
  echo -e "${CYAN}You'll be prompted for:${NC}"
  echo "  - HTTP port (default: 80)"
  echo "  - HTTPS port (default: 443)"
  echo "  - Encryption key"
  echo "  - Hostname"
  echo ""
  echo -e "${YELLOW}Press Ctrl+C to cancel, or Enter to continue...${NC}"
  read -r

  # Create install directory
  mkdir -p "$INSTALL_DIR"
  cd "$INSTALL_DIR"

  log_info "Running Appwrite installer..."
  echo ""

  # Run official installer
  docker run -it --rm \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --volume "$(pwd)":/usr/src/code/appwrite:rw \
    --entrypoint="install" \
    "appwrite/appwrite:${APPWRITE_VERSION}"

  echo ""
  log_success "Appwrite installation complete!"
}

# ============================================
# Post-install info
# ============================================
post_install() {
  echo ""
  echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
  echo -e "${GREEN}  Appwrite Full Installation Complete${NC}"
  echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
  echo ""
  echo -e "${CYAN}Installation directory:${NC}"
  echo "  $INSTALL_DIR"
  echo ""
  echo -e "${CYAN}Generated files:${NC}"
  echo "  $INSTALL_DIR/docker-compose.yml"
  echo "  $INSTALL_DIR/.env"
  echo ""
  echo -e "${CYAN}Commands:${NC}"
  echo -e "  ${YELLOW}Start:${NC}    cd $INSTALL_DIR && docker compose up -d"
  echo -e "  ${YELLOW}Stop:${NC}     cd $INSTALL_DIR && docker compose down"
  echo -e "  ${YELLOW}Logs:${NC}     cd $INSTALL_DIR && docker compose logs -f"
  echo -e "  ${YELLOW}Status:${NC}   cd $INSTALL_DIR && docker compose ps"
  echo ""
  echo -e "${CYAN}Console:${NC} Check your configured hostname (default: http://localhost)"
  echo ""
  echo -e "${YELLOW}Note:${NC} This is separate from the minimal Appwrite in 'codeagent start'."
  echo "      They can run side-by-side on different ports."
  echo ""
}

# ============================================
# Upgrade existing installation
# ============================================
upgrade_appwrite() {
  if [ ! -f "$INSTALL_DIR/docker-compose.yml" ]; then
    log_error "No existing installation found at $INSTALL_DIR"
    log_info "Run this script without --upgrade to install first."
    exit 1
  fi

  log_info "Upgrading Appwrite to ${APPWRITE_VERSION}..."
  cd "$INSTALL_DIR"

  # Stop current installation
  docker compose down

  # Run upgrade
  docker run -it --rm \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --volume "$(pwd)":/usr/src/code/appwrite:rw \
    --entrypoint="upgrade" \
    "appwrite/appwrite:${APPWRITE_VERSION}"

  log_success "Upgrade complete!"
  echo ""
  echo "Start with: cd $INSTALL_DIR && docker compose up -d"
}

# ============================================
# Usage
# ============================================
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Install the full Appwrite BaaS (~25 services)"
  echo ""
  echo "Options:"
  echo "  --upgrade     Upgrade existing installation"
  echo "  --version V   Use specific Appwrite version (default: ${APPWRITE_VERSION})"
  echo "  --help        Show this help"
  echo ""
  echo "Environment:"
  echo "  APPWRITE_VERSION    Appwrite version to install"
  echo "  CODEAGENT_HOME      Installation base directory"
  echo ""
  echo "Examples:"
  echo "  $0                           # Interactive install"
  echo "  $0 --upgrade                 # Upgrade existing"
  echo "  $0 --version 1.7.0           # Install specific version"
  echo ""
}

# ============================================
# Main
# ============================================
main() {
  local upgrade=false

  while [[ $# -gt 0 ]]; do
    case $1 in
      --upgrade)
        upgrade=true
        shift
        ;;
      --version)
        APPWRITE_VERSION="$2"
        shift 2
        ;;
      --help | -h)
        usage
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        usage
        exit 1
        ;;
    esac
  done

  echo ""
  echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}║       Appwrite Full BaaS Installer (v${APPWRITE_VERSION})            ║${NC}"
  echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
  echo ""

  preflight

  if [ "$upgrade" = true ]; then
    upgrade_appwrite
  else
    install_appwrite
    post_install
  fi
}

main "$@"
