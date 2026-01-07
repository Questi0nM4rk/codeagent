#!/bin/bash
# ============================================
# CodeAgent Development Tools Installer
# Installs linters, formatters, security scanners
# ============================================
#
# Uses yay (AUR helper) for Arch Linux
# Supports: --minimal, --full, --check flags
#
# Usage:
#   ./install-tools.sh           # Install recommended tools
#   ./install-tools.sh --minimal # Only essential tools
#   ./install-tools.sh --full    # All tools including optional
#   ./install-tools.sh --check   # Check what's installed

set -e

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
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() { echo -e "\n${CYAN}=== $1 ===${NC}"; }

# ============================================
# Tool Definitions
# ============================================

# Essential tools (--minimal)
ESSENTIAL_PACMAN=(
    "jq"              # JSON processor
    "git"             # Version control
    "base-devel"      # Build essentials
)

ESSENTIAL_YAY=(
    "shellcheck"      # Shell script linter
    "shfmt"           # Shell script formatter
)

# Recommended tools (default)
RECOMMENDED_PACMAN=(
    "python"          # Python runtime
    "python-pip"      # Python package manager
    "nodejs"          # Node.js runtime
    "npm"             # Node package manager
    "rust"            # Rust toolchain (includes cargo)
    "go"              # Go toolchain
    "clang"           # C/C++ compiler + tools
    "cmake"           # Build system
    "valgrind"        # Memory debugger
    "docker"          # Container runtime
    "docker-compose"  # Container orchestration
)

RECOMMENDED_YAY=(
    "semgrep-bin"     # Universal security scanner
    "hadolint-bin"    # Dockerfile linter
    "yamllint"        # YAML linter
    "luacheck"        # Lua linter
    "stylua"          # Lua formatter
    "cppcheck"        # C/C++ static analyzer
    "yq"              # YAML processor
)

# Python tools (pip)
PYTHON_TOOLS=(
    "ruff"            # Python linter (fast)
    "mypy"            # Python type checker
    "bandit"          # Python security linter
    "black"           # Python formatter
    "isort"           # Python import sorter
    "pytest"          # Python testing
    "pytest-cov"      # Coverage plugin
)

# Rust tools (cargo)
RUST_TOOLS=(
    "cargo-audit"     # Rust security auditor
    "cargo-watch"     # Rust file watcher
    "cargo-tarpaulin" # Rust coverage (optional)
)

# Node tools (npm global)
NODE_TOOLS=(
    "eslint"          # JavaScript linter
    "typescript"      # TypeScript compiler
    "prettier"        # Code formatter
    "@biomejs/biome"  # Fast linter (Rust-based)
)

# Full installation extras (--full)
FULL_PACMAN=(
    "lua"             # Lua runtime
    "luarocks"        # Lua package manager
    "dotnet-sdk"      # .NET SDK
    "gopls"           # Go language server
    "rust-analyzer"   # Rust language server
    "clang-tools-extra" # clang-tidy, clang-format
    "gdb"             # GNU debugger
    "strace"          # System call tracer
    "perf"            # Performance analyzer
)

FULL_YAY=(
    "golangci-lint"   # Go meta-linter
    "trivy-bin"       # Container security scanner
    "gitleaks"        # Git secrets scanner
    "actionlint"      # GitHub Actions linter
    "taplo-cli"       # TOML formatter
    "deno"            # Deno runtime
    "bun-bin"         # Bun runtime
)

# ============================================
# Helper Functions
# ============================================

check_yay() {
    if ! command -v yay &> /dev/null; then
        log_error "yay not found. Please install yay first:"
        echo "  git clone https://aur.archlinux.org/yay.git"
        echo "  cd yay && makepkg -si"
        exit 1
    fi
}

check_tool() {
    local tool="$1"
    local cmd="${2:-$1}"

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>/dev/null | head -1 || echo "installed")
        echo -e "  ${GREEN}✓${NC} $tool: $version"
        return 0
    else
        echo -e "  ${RED}✗${NC} $tool: not installed"
        return 1
    fi
}

install_pacman() {
    local packages=("$@")
    local to_install=()

    for pkg in "${packages[@]}"; do
        if ! pacman -Qi "$pkg" &> /dev/null; then
            to_install+=("$pkg")
        fi
    done

    if [ ${#to_install[@]} -gt 0 ]; then
        log_info "Installing pacman packages: ${to_install[*]}"
        sudo pacman -S --needed --noconfirm "${to_install[@]}"
    else
        log_info "All pacman packages already installed"
    fi
}

install_yay() {
    local packages=("$@")
    local to_install=()

    for pkg in "${packages[@]}"; do
        if ! yay -Qi "$pkg" &> /dev/null; then
            to_install+=("$pkg")
        fi
    done

    if [ ${#to_install[@]} -gt 0 ]; then
        log_info "Installing AUR packages: ${to_install[*]}"
        yay -S --needed --noconfirm "${to_install[@]}"
    else
        log_info "All AUR packages already installed"
    fi
}

install_pip() {
    local packages=("$@")

    if ! command -v pip &> /dev/null; then
        log_warn "pip not found, skipping Python tools"
        return
    fi

    log_info "Installing Python tools: ${packages[*]}"
    pip install --user --quiet --upgrade "${packages[@]}" 2>/dev/null || {
        log_warn "Some Python packages failed to install"
    }
}

install_cargo() {
    local packages=("$@")

    if ! command -v cargo &> /dev/null; then
        log_warn "cargo not found, skipping Rust tools"
        return
    fi

    for pkg in "${packages[@]}"; do
        if ! cargo install --list | grep -q "^$pkg "; then
            log_info "Installing cargo: $pkg"
            cargo install "$pkg" 2>/dev/null || log_warn "Failed to install $pkg"
        fi
    done
}

install_npm() {
    local packages=("$@")

    if ! command -v npm &> /dev/null; then
        log_warn "npm not found, skipping Node tools"
        return
    fi

    log_info "Installing npm tools: ${packages[*]}"
    npm install -g "${packages[@]}" 2>/dev/null || {
        log_warn "Some npm packages failed to install (may need sudo)"
    }
}

# ============================================
# Check Mode
# ============================================
check_all_tools() {
    log_section "Essential Tools"
    check_tool "jq"
    check_tool "git"
    check_tool "shellcheck"
    check_tool "shfmt"

    log_section "Shell & Scripts"
    check_tool "bash"
    check_tool "zsh"

    log_section "Python"
    check_tool "python" "python3"
    check_tool "pip" "pip3"
    check_tool "ruff"
    check_tool "mypy"
    check_tool "bandit"
    check_tool "black"
    check_tool "pytest"

    log_section "JavaScript/TypeScript"
    check_tool "node"
    check_tool "npm"
    check_tool "eslint"
    check_tool "tsc" "tsc"
    check_tool "prettier"
    check_tool "biome"

    log_section "Rust"
    check_tool "rustc"
    check_tool "cargo"
    check_tool "cargo-audit" "cargo-audit"
    check_tool "clippy" "cargo-clippy"
    check_tool "rustfmt" "rustfmt"

    log_section "Go"
    check_tool "go"
    check_tool "golangci-lint"

    log_section "C/C++"
    check_tool "clang"
    check_tool "clang-format"
    check_tool "clang-tidy"
    check_tool "cppcheck"
    check_tool "valgrind"
    check_tool "cmake"

    log_section "Lua"
    check_tool "lua"
    check_tool "luacheck"
    check_tool "stylua"

    log_section ".NET"
    check_tool "dotnet"

    log_section "Security"
    check_tool "semgrep"
    check_tool "bandit"
    check_tool "trivy"
    check_tool "gitleaks"

    log_section "Docker & Containers"
    check_tool "docker"
    check_tool "docker-compose" "docker"
    check_tool "hadolint"

    log_section "Config Files"
    check_tool "yamllint"
    check_tool "yq"
    check_tool "jq"
    check_tool "taplo"

    echo ""
}

# ============================================
# Installation Modes
# ============================================
install_minimal() {
    log_section "Installing Essential Tools"

    install_pacman "${ESSENTIAL_PACMAN[@]}"
    install_yay "${ESSENTIAL_YAY[@]}"

    log_success "Minimal installation complete"
}

install_recommended() {
    log_section "Installing Essential Tools"
    install_pacman "${ESSENTIAL_PACMAN[@]}"
    install_yay "${ESSENTIAL_YAY[@]}"

    log_section "Installing Recommended System Packages"
    install_pacman "${RECOMMENDED_PACMAN[@]}"
    install_yay "${RECOMMENDED_YAY[@]}"

    log_section "Installing Python Tools"
    install_pip "${PYTHON_TOOLS[@]}"

    log_section "Installing Rust Tools"
    install_cargo "${RUST_TOOLS[@]}"

    log_section "Installing Node Tools"
    install_npm "${NODE_TOOLS[@]}"

    log_success "Recommended installation complete"
}

install_full() {
    # First do recommended
    install_recommended

    log_section "Installing Full Extras"
    install_pacman "${FULL_PACMAN[@]}"
    install_yay "${FULL_YAY[@]}"

    log_success "Full installation complete"
}

# ============================================
# Main
# ============================================
main() {
    local mode="recommended"

    while [[ $# -gt 0 ]]; do
        case $1 in
            --minimal|-m)
                mode="minimal"
                shift
                ;;
            --full|-f)
                mode="full"
                shift
                ;;
            --check|-c)
                mode="check"
                shift
                ;;
            -h|--help)
                echo "CodeAgent Development Tools Installer"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --minimal, -m  Install only essential tools (shellcheck, shfmt, jq)"
                echo "  --full, -f     Install all tools including extras"
                echo "  --check, -c    Check what tools are installed"
                echo "  -h, --help     Show this help"
                echo ""
                echo "Default: Install recommended tools for all supported languages"
                echo ""
                echo "Tool Categories:"
                echo "  Essential:    shellcheck, shfmt, jq, git"
                echo "  Python:       ruff, mypy, bandit, black, pytest"
                echo "  Rust:         cargo-audit, clippy, rustfmt"
                echo "  JavaScript:   eslint, typescript, prettier, biome"
                echo "  C/C++:        clang, cppcheck, valgrind, cmake"
                echo "  Lua:          luacheck, stylua"
                echo "  Go:           golangci-lint"
                echo "  Security:     semgrep, bandit, trivy, gitleaks"
                echo "  Docker:       hadolint"
                echo "  Config:       yamllint, yq, taplo"
                echo ""
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           CodeAgent Development Tools Installer                ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    if [ "$mode" = "check" ]; then
        check_all_tools
        exit 0
    fi

    # Check yay is available
    check_yay

    case $mode in
        minimal)
            log_info "Mode: Minimal (essential tools only)"
            install_minimal
            ;;
        recommended)
            log_info "Mode: Recommended (all common tools)"
            install_recommended
            ;;
        full)
            log_info "Mode: Full (everything including extras)"
            install_full
            ;;
    esac

    echo ""
    log_section "Installation Summary"
    log_info "Run '$0 --check' to verify installed tools"
    echo ""
}

main "$@"
