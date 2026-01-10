#!/bin/bash
set -e

# ============================================
# CodeAgent Installer
# Research-Backed Autonomous Coding Framework
# ============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
BIN_DIR="$HOME/.local/bin"
REPO_URL="${CODEAGENT_REPO:-https://github.com/Questi0nM4rk/codeagent.git}"
VERSION="0.1.0"

# ============================================
# Banner
# ============================================
print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║      ██████╗ ██████╗ ██████╗ ███████╗ █████╗  ██████╗        ║"
    echo "║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝        ║"
    echo "║     ██║     ██║   ██║██║  ██║█████╗  ███████║██║  ███╗       ║"
    echo "║     ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██║██║   ██║       ║"
    echo "║     ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║╚██████╔╝       ║"
    echo "║      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝        ║"
    echo "║                                                               ║"
    echo "║          Research-Backed Autonomous Coding Framework          ║"
    echo "║                        v${VERSION}                                  ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ============================================
# Utility Functions
# ============================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    local cmd=$1
    local name=${2:-$1}
    local required=${3:-true}

    if command -v "$cmd" &> /dev/null; then
        log_success "$name found"
        return 0
    else
        if [ "$required" = true ]; then
            log_error "$name not found. Please install it first."
            return 1
        else
            log_warn "$name not found (optional)"
            return 0
        fi
    fi
}

# Install Claude Code CLI from Anthropic's official installer
install_claude_cli() {
    log_info "Installing Claude Code CLI..."

    if command -v claude &> /dev/null; then
        log_success "Claude Code CLI already installed"
        return 0
    fi

    # Use Anthropic's official installer
    if curl -fsSL https://claude.ai/install.sh | bash; then
        # Add to PATH for current session
        export PATH="$HOME/.claude/bin:$PATH"

        if command -v claude &> /dev/null; then
            log_success "Claude Code CLI installed successfully"
            return 0
        else
            log_warn "Claude Code CLI installed but not in PATH - restart your shell"
            return 0
        fi
    else
        log_warn "Failed to install Claude Code CLI - you can install it manually later"
        log_info "Visit: https://claude.ai/code"
        return 1
    fi
}

# ============================================
# Requirement Checks
# ============================================
check_requirements() {
    echo ""
    log_info "Checking requirements..."
    echo ""

    local failed=false

    # Required
    check_command docker "Docker" true || failed=true
    check_command node "Node.js" true || failed=true
    check_command python3 "Python 3" true || failed=true
    check_command git "Git" true || failed=true

    # Docker Compose v2
    if docker compose version &> /dev/null; then
        log_success "Docker Compose v2 found"
    else
        log_error "Docker Compose v2 not found"
        failed=true
    fi

    # Install Claude Code CLI if not found
    if ! command -v claude &> /dev/null; then
        log_info "Claude Code CLI not found - installing..."
        install_claude_cli || log_warn "Continuing without Claude CLI"
    else
        log_success "Claude Code CLI found"
    fi

    if [ "$failed" = true ]; then
        echo ""
        log_error "Missing required dependencies. Please install them and try again."
        exit 1
    fi

    echo ""
    log_success "All requirements satisfied"
}

# ============================================
# Installation
# ============================================
install_codeagent() {
    echo ""
    log_info "Installing CodeAgent to $INSTALL_DIR..."

    # Create directories
    mkdir -p "$BIN_DIR"
    mkdir -p "$HOME/.claude"

    # Clone or update
    if [ -d "$INSTALL_DIR" ]; then
        log_info "Updating existing installation..."

        # Local install mode - copy files
        if [ "$local_install" = true ]; then
            log_info "Updating from local source..."
            local script_dir
            script_dir="$(cd "$(dirname "$0")" && pwd)"
            # Sync local files (exclude .git, venv, and data)
            rsync -av --exclude='.git' --exclude='venv' --exclude='data' \
                "$script_dir"/ "$INSTALL_DIR"/ 2>/dev/null || \
                cp -r "$script_dir"/* "$INSTALL_DIR"/ 2>/dev/null || {
                    log_error "Failed to update local files"
                    exit 1
                }
            log_success "Updated from local source"
        # Git mode
        elif [ -d "$INSTALL_DIR/.git" ]; then
            cd "$INSTALL_DIR"
            if [ "$force_reinstall" = true ]; then
                # Force mode: discard all local changes and reset to remote
                log_warn "Force mode: discarding local changes in $INSTALL_DIR..."
                git fetch origin 2>/dev/null || true
                git reset --hard origin/main 2>/dev/null || git reset --hard origin/master 2>/dev/null || {
                    log_warn "Git reset failed, continuing anyway..."
                }
                log_success "Reset to latest remote version"
            else
                # Normal mode: try to pull, warn if dirty
                if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
                    log_warn "Local changes detected in $INSTALL_DIR"
                    log_warn "Use --force to discard changes and update"
                fi
                git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || {
                    log_warn "Git pull failed (local changes?). Use --force to overwrite."
                }
            fi
        else
            log_warn "$INSTALL_DIR exists but is not a git repo"
        fi
    else
        log_info "Cloning repository..."
        if [ "$local_install" = true ] || [ "$REPO_URL" = "https://github.com/YOUR_USERNAME/codeagent.git" ]; then
            # Local install mode (development)
            log_info "Running in local development mode..."
            local script_dir
            script_dir="$(cd "$(dirname "$0")" && pwd)"
            mkdir -p "$INSTALL_DIR"
            cp -r "$script_dir"/* "$INSTALL_DIR/" 2>/dev/null || {
                log_error "Failed to copy files. Run from the codeagent directory."
                exit 1
            }
            log_success "Copied local files to $INSTALL_DIR"
        else
            git clone "$REPO_URL" "$INSTALL_DIR"
        fi
    fi

    cd "$INSTALL_DIR"

    # Make scripts executable
    log_info "Setting up CLI commands..."
    chmod +x bin/* 2>/dev/null || true
    chmod +x scripts/* 2>/dev/null || true
    chmod +x mcps/*.sh 2>/dev/null || true
    chmod +x install.sh uninstall.sh 2>/dev/null || true

    # Create symlinks in bin directory
    for script in bin/*; do
        if [ -f "$script" ]; then
            local name=$(basename "$script")
            ln -sf "$INSTALL_DIR/$script" "$BIN_DIR/$name"
            log_success "Linked $name"
        fi
    done

    # Install Python dependencies for custom MCPs
    log_info "Setting up Python virtual environment..."

    # Create venv in install directory
    VENV_DIR="$INSTALL_DIR/venv"
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "Created virtual environment at $VENV_DIR"
    else
        log_info "Virtual environment already exists"
    fi

    # Install packages in venv
    log_info "Installing Python dependencies in venv..."
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip 2>/dev/null || true
    "$VENV_DIR/bin/pip" install --quiet \
        mcp \
        openai \
        httpx \
        pydantic 2>/dev/null && log_success "Python dependencies installed" || log_warn "Some Python packages failed to install"

    # Install custom MCP dependencies (tree-sitter etc.)
    log_info "Installing custom MCP dependencies..."
    "$VENV_DIR/bin/pip" install --quiet \
        tree-sitter \
        tree-sitter-c-sharp \
        tree-sitter-cpp \
        tree-sitter-rust \
        tree-sitter-lua \
        tree-sitter-bash \
        tree-sitter-python \
        tree-sitter-typescript \
        tree-sitter-javascript \
        tree-sitter-go 2>/dev/null && log_success "Tree-sitter parsers installed (9 languages)" || log_warn "Some tree-sitter packages failed (optional)"
}

# ============================================
# Shell Configuration
# ============================================
configure_shell() {
    echo ""
    log_info "Configuring shell..."

    local shell_rc=""
    local shell_name=""

    # Detect shell
    if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
        shell_rc="$HOME/.zshrc"
        shell_name="zsh"
    elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
        shell_rc="$HOME/.bashrc"
        shell_name="bash"
    fi

    if [ -n "$shell_rc" ] && [ -f "$shell_rc" ]; then
        # Add to PATH if not already there
        if ! grep -q "CODEAGENT_HOME" "$shell_rc"; then
            echo "" >> "$shell_rc"
            echo "# CodeAgent" >> "$shell_rc"
            echo "export CODEAGENT_HOME=\"$INSTALL_DIR\"" >> "$shell_rc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_rc"
            log_success "Added CodeAgent to $shell_rc"
        else
            log_info "CodeAgent already in $shell_rc"
        fi
    fi

    # Export for current session
    export CODEAGENT_HOME="$INSTALL_DIR"
    export PATH="$BIN_DIR:$PATH"
}

# ============================================
# Claude Code Configuration Handling
# ============================================
# Delegated to scripts/install-claude-config.sh for:
# - Skills, commands, hooks installation with validation
# - Settings.json from template with merge support
# - CLAUDE.md from template with merge support
# - Update detection (skip unchanged files)
# - Force reinstall support
# ============================================
setup_global_config() {
    # Export variables for sub-script
    export CODEAGENT_HOME="$INSTALL_DIR"
    export CODEAGENT_FORCE="${CODEAGENT_FORCE_REINSTALL:-false}"
    export CODEAGENT_AUTO_YES="${CODEAGENT_AUTO_YES:-false}"
    export RED GREEN YELLOW BLUE CYAN NC

    # Call the dedicated config installer
    if [ -f "$INSTALL_DIR/scripts/install-claude-config.sh" ]; then
        bash "$INSTALL_DIR/scripts/install-claude-config.sh"
    else
        log_error "Config installer not found: $INSTALL_DIR/scripts/install-claude-config.sh"
        log_warn "Falling back to basic installation..."
        fallback_claude_config
    fi
}

# Fallback if sub-script is missing (shouldn't happen)
fallback_claude_config() {
    mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands" "$HOME/.claude/hooks" "$HOME/.claude/agents"

    # Copy skills
    if [ -d "$INSTALL_DIR/framework/skills" ]; then
        cp -r "$INSTALL_DIR/framework/skills/"* "$HOME/.claude/skills/" 2>/dev/null || true
    fi

    # Copy commands
    if [ -d "$INSTALL_DIR/framework/commands" ]; then
        cp "$INSTALL_DIR/framework/commands/"*.md "$HOME/.claude/commands/" 2>/dev/null || true
    fi

    # Copy hooks
    if [ -d "$INSTALL_DIR/framework/hooks" ]; then
        cp "$INSTALL_DIR/framework/hooks/"*.sh "$HOME/.claude/hooks/" 2>/dev/null || true
        chmod +x "$HOME/.claude/hooks/"*.sh 2>/dev/null || true
    fi

    # Copy agents
    if [ -d "$INSTALL_DIR/framework/agents" ]; then
        cp "$INSTALL_DIR/framework/agents/"*.md "$HOME/.claude/agents/" 2>/dev/null || true
    fi

    # Copy settings from template
    if [ -f "$INSTALL_DIR/framework/settings.json.template" ]; then
        cp "$INSTALL_DIR/framework/settings.json.template" "$HOME/.claude/settings.json"
    fi

    # Copy CLAUDE.md from template
    if [ -f "$INSTALL_DIR/templates/CLAUDE.md.template" ]; then
        cp "$INSTALL_DIR/templates/CLAUDE.md.template" "$HOME/.claude/CLAUDE.md"
    fi

    log_success "Basic Claude Code configuration installed"
}

# ============================================
# API Key Setup (Interactive)
# ============================================
setup_api_keys() {
    echo ""
    log_info "Configuring API keys..."

    # .env file location (Docker Compose reads this automatically)
    local env_file="$INSTALL_DIR/.env"

    # Create .env header if file doesn't exist
    if [ ! -f "$env_file" ]; then
        cat > "$env_file" << 'ENVHEADER'
# CodeAgent API Keys
# ===================
# This file is read by Docker Compose automatically.
# For CLI tools, add to your shell config:
#   source ~/.codeagent/.env
ENVHEADER
    fi

    # Helper to set a key (removes duplicates, adds new value)
    set_env_key() {
        local key="$1"
        local value="$2"
        sed -i "/^$key=/d" "$env_file" 2>/dev/null || true
        echo "$key=$value" >> "$env_file"
    }

    # Helper to prompt for a key
    prompt_for_key() {
        local key_name="$1"
        local description="$2"
        local required="$3"
        local example="$4"

        echo ""

        # Check if key already exists in .env file
        local existing_value=""
        if grep -q "^$key_name=" "$env_file" 2>/dev/null; then
            existing_value=$(grep "^$key_name=" "$env_file" | tail -1 | cut -d= -f2-)
        fi

        # If key exists and is valid, skip
        if [ -n "$existing_value" ] && [ "$existing_value" != "REPLACE_WITH_YOUR_KEY" ]; then
            log_success "$key_name: configured"
            return
        fi

        # Check environment variable
        if [ -n "${!key_name}" ]; then
            set_env_key "$key_name" "${!key_name}"
            log_success "$key_name: copied from environment"
            return
        fi

        # Skip interactive prompt if non-interactive mode
        if [ "$auto_yes" = "true" ] || [ ! -t 0 ]; then
            if [ "$required" = "required" ]; then
                set_env_key "$key_name" "REPLACE_WITH_YOUR_KEY"
                log_warn "$key_name: placeholder added - run 'codeagent-config store $key_name <value>' to set it"
            fi
            return
        fi

        # Prompt user
        if [ "$required" = "required" ]; then
            log_warn "$key_name not found - $description"
            echo -n "  Enter $key_name (e.g., $example): "
            read -r new_value
            if [ -n "$new_value" ]; then
                set_env_key "$key_name" "$new_value"
                log_success "$key_name: saved"
            else
                set_env_key "$key_name" "REPLACE_WITH_YOUR_KEY"
                log_warn "$key_name: placeholder added - edit $env_file to set it"
            fi
        else
            log_info "$key_name (optional) - $description"
            echo -n "  Enter $key_name or press Enter to skip: "
            read -r new_value
            if [ -n "$new_value" ]; then
                set_env_key "$key_name" "$new_value"
                log_success "$key_name: saved"
            fi
        fi
    }

    echo ""
    echo -e "${CYAN}API keys are stored in $env_file${NC}"
    echo ""

    # Prompt for each key
    echo -e "${BLUE}Required:${NC}"
    prompt_for_key "OPENAI_API_KEY" "needed for A-MEM metadata generation (~\$0.01/month)" "required" "sk-..."

    echo ""
    echo -e "${BLUE}Optional:${NC}"
    prompt_for_key "GITHUB_TOKEN" "enables GitHub MCP integration" "optional" "ghp_..."
    prompt_for_key "TAVILY_API_KEY" "enables web research MCP" "optional" "tvly-..."

    echo ""
    echo -e "${CYAN}To use keys in your shell, add to ~/.zshrc or ~/.bashrc:${NC}"
    echo -e "  ${YELLOW}source $env_file${NC}"
    echo ""
}

# ============================================
# MCP Configuration
# ============================================
install_mcps() {
    local force_flag="$1"

    echo ""
    log_info "Configuring MCP servers..."

    # Export variables for sub-script
    export CODEAGENT_HOME="$INSTALL_DIR"
    export CODEAGENT_NO_DOCKER="${skip_docker:-false}"

    # Set force based on argument or global flag
    if [ "$force_flag" = "--force" ] || [ "$force_reinstall" = "true" ]; then
        export CODEAGENT_FORCE="true"
    else
        export CODEAGENT_FORCE="false"
    fi

    # CODEAGENT_RESET is already exported from main()

    if [ -f "$INSTALL_DIR/mcps/install-mcps.sh" ]; then
        bash "$INSTALL_DIR/mcps/install-mcps.sh"
    else
        log_warn "MCP installer not found. MCPs will need manual configuration."
    fi
}

# ============================================
# Start Infrastructure
# ============================================
start_infrastructure() {
    echo ""
    log_info "Starting CodeAgent infrastructure..."

    # Docker Compose reads API keys from .env file automatically (via env_file directive)
    # No need to export or read keys here

    # Start Docker containers
    cd "$INSTALL_DIR/infrastructure"

    # Check if containers exist but are unhealthy - recreate them
    local needs_recreate=false
    for container in codeagent-qdrant; do
        local status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
        if [ "$status" = "unhealthy" ]; then
            log_warn "$container is unhealthy, will recreate..."
            needs_recreate=true
        fi
    done

    if [ "$needs_recreate" = true ]; then
        log_info "Stopping unhealthy containers..."
        docker compose down 2>/dev/null || true
        sleep 2
    fi

    log_info "Starting Docker containers..."
    docker compose up -d --remove-orphans 2>/dev/null || {
        log_warn "Docker compose failed. Try running 'codeagent start' manually."
        return 1
    }

    # Wait for containers to be healthy
    log_info "Waiting for services to be healthy..."
    local max_wait=120
    local waited=0

    while [ $waited -lt $max_wait ]; do
        local qdrant_healthy=$(docker inspect --format='{{.State.Health.Status}}' codeagent-qdrant 2>/dev/null || echo "none")

        if [ "$qdrant_healthy" = "healthy" ]; then
            log_success "All services are healthy!"
            return 0
        fi

        sleep 5
        waited=$((waited + 5))
        echo -n "."
    done

    echo ""
    log_warn "Some services may not be fully healthy yet. Check with 'codeagent status'"
    return 0
}

# ============================================
# Verify Installation
# ============================================
verify_installation() {
    echo ""
    log_info "Verifying installation..."

    local all_ok=true

    # Check CLI commands
    if [ -x "$BIN_DIR/codeagent" ]; then
        log_success "CLI commands installed"
    else
        log_warn "CLI commands may need PATH update"
        all_ok=false
    fi

    # Check skills
    if [ -d "$HOME/.claude/skills" ] && [ "$(ls -A $HOME/.claude/skills 2>/dev/null)" ]; then
        log_success "Skills installed ($(ls -d $HOME/.claude/skills/*/ 2>/dev/null | wc -l) skills)"
    else
        log_warn "Skills not found"
        all_ok=false
    fi

    # Check commands
    if [ -d "$HOME/.claude/commands" ] && [ "$(ls -A $HOME/.claude/commands 2>/dev/null)" ]; then
        log_success "Commands installed ($(ls $HOME/.claude/commands/*.md 2>/dev/null | wc -l) commands)"
    else
        log_warn "Commands not found"
        all_ok=false
    fi

    # Check hooks
    if [ -d "$HOME/.claude/hooks" ] && [ "$(ls -A $HOME/.claude/hooks/*.sh 2>/dev/null)" ]; then
        log_success "Hooks installed"
    else
        log_warn "Hooks not found"
        all_ok=false
    fi

    # Check agents
    if [ -d "$HOME/.claude/agents" ] && [ "$(ls -A $HOME/.claude/agents/*.md 2>/dev/null)" ]; then
        log_success "Agents installed ($(ls $HOME/.claude/agents/*.md 2>/dev/null | wc -l) agents)"
    else
        log_warn "Agents not found"
        all_ok=false
    fi

    # Check Docker containers
    if docker ps | grep -q "codeagent-qdrant"; then
        log_success "Qdrant container running"
    else
        log_warn "Qdrant not running"
        all_ok=false
    fi

    # Check A-MEM storage
    if [ -d "$HOME/.codeagent/memory" ] || mkdir -p "$HOME/.codeagent/memory"; then
        log_success "A-MEM storage ready"
    else
        log_warn "A-MEM storage not accessible"
        all_ok=false
    fi

    # Check custom MCPs (reflection is the only custom Python MCP)
    if [ -f "$INSTALL_DIR/mcps/reflection-mcp/pyproject.toml" ]; then
        log_success "Custom MCPs installed (reflection)"
    else
        log_warn "Custom MCPs not found"
        all_ok=false
    fi

    echo ""
    if [ "$all_ok" = true ]; then
        log_success "All components verified successfully!"
    else
        log_warn "Some components need attention"
    fi
}

# ============================================
# Print Success
# ============================================
print_success() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Installation Complete!                            ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}CodeAgent is ready to use!${NC}"
    echo ""
    echo -e "  ${BLUE}1.${NC} Restart your shell or run:"
    echo -e "     ${YELLOW}source ~/.zshrc${NC}  (or ~/.bashrc)"
    echo ""
    echo -e "  ${BLUE}2.${NC} Initialize in your project:"
    echo -e "     ${YELLOW}cd /your/project${NC}"
    echo -e "     ${YELLOW}codeagent init${NC}"
    echo ""
    echo -e "  ${BLUE}3.${NC} Start coding with Claude Code:"
    echo -e "     ${YELLOW}/scan${NC}              Build knowledge graph"
    echo -e "     ${YELLOW}/plan \"task\"${NC}       Research & design"
    echo -e "     ${YELLOW}/implement${NC}         TDD implementation"
    echo -e "     ${YELLOW}/review${NC}            Validate changes"
    echo ""
    echo -e "${CYAN}Useful commands:${NC}"
    echo -e "  ${YELLOW}codeagent status${NC}   Check service health"
    echo -e "  ${YELLOW}codeagent stop${NC}     Stop infrastructure"
    echo -e "  ${YELLOW}codeagent start${NC}    Start infrastructure"
    echo ""
    echo -e "Documentation: ${CYAN}$INSTALL_DIR/Docs/${NC}"
    echo ""
}

# ============================================
# Main
# ============================================
main() {
    # Parse arguments
    local skip_docker=false
    local force_reinstall=false
    local reset_data=false
    local auto_yes=false
    local local_install=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-docker)
                skip_docker=true
                shift
                ;;
            --force|-f)
                force_reinstall=true
                shift
                ;;
            --reset)
                reset_data=true
                force_reinstall=true  # Reset implies force
                shift
                ;;
            -y|--yes)
                auto_yes=true
                shift
                ;;
            --local)
                local_install=true
                shift
                ;;
            -h|--help)
                echo "CodeAgent Installer"
                echo ""
                echo "Usage: ./install.sh [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --no-docker    Skip Docker container setup"
                echo "  --force, -f    Force reinstall MCPs and recreate containers (preserves data)"
                echo "  --reset        Delete ALL data (A-MEM memories, vector embeddings)"
                echo "  -y, --yes      Auto-accept prompts (backup existing config)"
                echo "  --local        Install from local source (development mode)"
                echo "  -h, --help     Show this help message"
                echo ""
                echo "Data Preservation:"
                echo "  --force        Keeps A-MEM memories intact"
                echo "  --reset        DELETES all A-MEM memories and vector embeddings"
                echo ""
                exit 0
                ;;
            *)
                shift
                ;;
        esac
    done

    # Export flags for sub-scripts
    export CODEAGENT_FORCE_REINSTALL="$force_reinstall"
    export CODEAGENT_RESET="$reset_data"

    print_banner

    # Warn about data deletion
    if [ "$reset_data" = "true" ]; then
        echo ""
        log_warn "=========================================="
        log_warn "  RESET MODE: All data will be deleted!"
        log_warn "  - A-MEM memories"
        log_warn "  - Qdrant vector embeddings"
        log_warn "=========================================="
        echo ""
        if [ "$auto_yes" != "true" ]; then
            read -p "Continue? [y/N]: " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Aborted."
                exit 0
            fi
        fi
    fi

    check_requirements
    install_codeagent
    configure_shell

    # Pass auto-yes to sub-scripts
    if [ "$auto_yes" = "true" ]; then
        export CODEAGENT_AUTO_YES=true
    fi
    setup_global_config
    setup_api_keys

    # Start infrastructure unless skipped
    if [ "$skip_docker" = false ]; then
        start_infrastructure
    else
        log_info "Skipping Docker setup (--no-docker flag)"
    fi

    # Install MCPs (pass --force if specified)
    if [ "$force_reinstall" = true ]; then
        install_mcps --force
    else
        install_mcps
    fi

    verify_installation
    print_success
}

# Run
main "$@"
