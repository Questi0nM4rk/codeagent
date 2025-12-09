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

    # Optional but recommended
    check_command claude "Claude Code CLI" false

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
        cd "$INSTALL_DIR"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
    else
        log_info "Cloning repository..."
        if [ "$REPO_URL" = "https://github.com/YOUR_USERNAME/codeagent.git" ]; then
            # Local install mode (development)
            log_info "Running in local development mode..."
            mkdir -p "$INSTALL_DIR"
            cp -r "$(dirname "$0")"/* "$INSTALL_DIR/" 2>/dev/null || {
                log_error "Failed to copy files. Run from the codeagent directory."
                exit 1
            }
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
        neo4j \
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
        tree-sitter-bash 2>/dev/null && log_success "Tree-sitter parsers installed" || log_warn "Some tree-sitter packages failed (optional)"
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
handle_claude_config() {
    echo ""
    log_info "Checking existing Claude Code configuration..."

    local backup_dir="$HOME/.claude-backup-$(date +%Y%m%d_%H%M%S)"
    local has_existing=false

    # Check for existing Claude Code config
    if [ -d "$HOME/.claude" ]; then
        if [ -f "$HOME/.claude/CLAUDE.md" ] || [ -f "$HOME/.claude/settings.json" ] || [ -d "$HOME/.claude/commands" ]; then
            has_existing=true
        fi
    fi

    if [ "$has_existing" = true ]; then
        echo ""
        echo -e "${YELLOW}Existing Claude Code configuration detected:${NC}"
        [ -f "$HOME/.claude/CLAUDE.md" ] && echo "  - ~/.claude/CLAUDE.md"
        [ -f "$HOME/.claude/settings.json" ] && echo "  - ~/.claude/settings.json"
        [ -d "$HOME/.claude/commands" ] && echo "  - ~/.claude/commands/"
        [ -d "$HOME/.claude/agents" ] && echo "  - ~/.claude/agents/"
        echo ""
        echo "Options:"
        echo "  1) Backup existing and install CodeAgent config"
        echo "  2) Merge (keep existing, add CodeAgent additions)"
        echo "  3) Skip (don't modify existing config)"
        echo ""
        read -p "Choose option [1/2/3]: " -n 1 -r config_choice
        echo ""

        case "$config_choice" in
            1)
                log_info "Backing up existing config to $backup_dir..."
                mkdir -p "$backup_dir"
                cp -r "$HOME/.claude"/* "$backup_dir/" 2>/dev/null || true
                log_success "Backup created at $backup_dir"
                # Remove existing config files to ensure fresh install
                rm -f "$HOME/.claude/CLAUDE.md" "$HOME/.claude/settings.json"
                rm -rf "$HOME/.claude/commands" "$HOME/.claude/skills" 2>/dev/null || true
                setup_fresh_claude_config
                ;;
            2)
                log_info "Merging configurations..."
                merge_claude_config
                ;;
            3)
                log_info "Skipping Claude Code config modification"
                log_warn "Note: CodeAgent global config will not be installed"
                ;;
            *)
                log_warn "Invalid choice, skipping config modification"
                ;;
        esac
    else
        setup_fresh_claude_config
    fi
}

setup_fresh_claude_config() {
    log_info "Setting up Claude Code configuration..."

    mkdir -p "$HOME/.claude/skills" "$HOME/.claude/commands" "$HOME/.claude/hooks"

    # Install global skills
    log_info "Installing global skills..."
    if [ -d "$INSTALL_DIR/framework/skills" ]; then
        cp -r "$INSTALL_DIR/framework/skills/"* "$HOME/.claude/skills/" 2>/dev/null || true
        log_success "Installed skills: researcher, architect, orchestrator, implementer, reviewer, learner"
    fi

    # Install global commands
    log_info "Installing global commands..."
    if [ -d "$INSTALL_DIR/framework/commands" ]; then
        cp "$INSTALL_DIR/framework/commands/"*.md "$HOME/.claude/commands/" 2>/dev/null || true
        log_success "Installed commands: /scan, /plan, /implement, /integrate, /review"
    fi

    # Install hooks
    log_info "Installing global hooks..."
    if [ -d "$INSTALL_DIR/framework/hooks" ]; then
        cp "$INSTALL_DIR/framework/hooks/"*.sh "$HOME/.claude/hooks/" 2>/dev/null || true
        chmod +x "$HOME/.claude/hooks/"*.sh 2>/dev/null || true
        log_success "Installed hooks: pre-commit, pre-push, post-implement, index-file"
    fi

    # Create global CLAUDE.md
    cat > "$HOME/.claude/CLAUDE.md" << 'GLOBALMD'
# Global Claude Configuration

## Identity
Senior software engineer. Direct communication. No fluff.

## Principles
1. Accuracy over speed - verify before acting
2. Test-first development - always TDD
3. Memory-first research - check project memory before external search
4. External validation - never self-review code

## Languages
Primary: C# (.NET 10), C++23, C, Rust, Lua
Shell: Bash, Zsh

## Response Style
- Concise, technical
- Code over prose
- Show commands, not just describe
- Include file:line references

## CodeAgent Integration
This configuration is managed by CodeAgent.
Run `codeagent init` in your project to set up project-specific agents and commands.
GLOBALMD
    log_success "Created ~/.claude/CLAUDE.md"

    # Create global settings.json (overwrite if exists since user chose fresh install)
    cat > "$HOME/.claude/settings.json" << 'SETTINGSJSON'
{
  "permissions": {
    "allow": [
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(node:*)",
      "Bash(python:*)",
      "Bash(python3:*)",
      "Bash(pip:*)",
      "Bash(pip3:*)",
      "Bash(docker:*)",
      "Bash(docker-compose:*)",
      "Bash(git:*)",
      "Bash(dotnet:*)",
      "Bash(cargo:*)",
      "Bash(rustc:*)",
      "Bash(cmake:*)",
      "Bash(make:*)",
      "Bash(lua:*)",
      "Bash(luarocks:*)",
      "Bash(busted:*)",
      "mcp__*"
    ],
    "deny": []
  }
}
SETTINGSJSON
    log_success "Created ~/.claude/settings.json"
}

merge_claude_config() {
    # Append CodeAgent section to existing CLAUDE.md if not present
    if [ -f "$HOME/.claude/CLAUDE.md" ]; then
        if ! grep -q "CodeAgent Integration" "$HOME/.claude/CLAUDE.md"; then
            cat >> "$HOME/.claude/CLAUDE.md" << 'APPENDMD'

## CodeAgent Integration
This configuration works with CodeAgent.
Run `codeagent init` in your project to set up project-specific agents and commands.
APPENDMD
            log_success "Added CodeAgent section to existing CLAUDE.md"
        else
            log_info "CodeAgent section already present in CLAUDE.md"
        fi
    else
        setup_fresh_claude_config
    fi
}

# ============================================
# Global Configuration (legacy - now calls handle_claude_config)
# ============================================
setup_global_config() {
    handle_claude_config
}

# ============================================
# API Key Setup (Interactive)
# ============================================
setup_api_keys() {
    echo ""
    log_info "Configuring API keys..."
    echo ""

    local env_file="$INSTALL_DIR/.env"

    # Create .env file if it doesn't exist
    if [ ! -f "$env_file" ]; then
        touch "$env_file"
        chmod 600 "$env_file"  # Secure permissions
    fi

    # Helper function to check and prompt for a key
    prompt_for_key() {
        local key_name="$1"
        local key_description="$2"
        local required="$3"
        local current_value="${!key_name}"

        # Check if already in environment
        if [ -n "$current_value" ]; then
            log_success "$key_name is set"
            # Save to .env if not already there
            if ! grep -q "^$key_name=" "$env_file" 2>/dev/null; then
                echo "$key_name=$current_value" >> "$env_file"
            fi
            return 0
        fi

        # Check if already in .env file
        if grep -q "^$key_name=" "$env_file" 2>/dev/null; then
            log_success "$key_name is configured"
            return 0
        fi

        # Prompt user
        echo ""
        if [ "$required" = "required" ]; then
            echo -e "${YELLOW}$key_name${NC} - $key_description ${RED}(required)${NC}"
        else
            echo -e "${YELLOW}$key_name${NC} - $key_description ${BLUE}(optional)${NC}"
        fi

        read -p "Enter $key_name (or press Enter to skip): " -r key_value

        if [ -n "$key_value" ]; then
            echo "$key_name=$key_value" >> "$env_file"
            log_success "$key_name saved to $env_file"
            export "$key_name=$key_value"
        else
            if [ "$required" = "required" ]; then
                log_warn "$key_name skipped - memory features will not work"
            else
                log_info "$key_name skipped"
            fi
        fi
    }

    echo -e "${CYAN}CodeAgent needs API keys for some features.${NC}"
    echo -e "${CYAN}Keys are stored securely in: $env_file${NC}"
    echo ""

    # Required key
    prompt_for_key "OPENAI_API_KEY" "For memory embeddings (~\$4/month)" "required"

    # Optional keys
    echo ""
    echo -e "${BLUE}Optional API keys (enhance functionality):${NC}"
    prompt_for_key "GITHUB_TOKEN" "For GitHub MCP integration" "optional"
    prompt_for_key "TAVILY_API_KEY" "For web research MCP" "optional"

    echo ""
    log_success "API key configuration complete"
    echo -e "Keys stored in: ${CYAN}$env_file${NC}"
    echo ""
}

# ============================================
# MCP Configuration
# ============================================
install_mcps() {
    echo ""
    log_info "Configuring MCP servers..."

    if [ -f "$INSTALL_DIR/mcps/install-mcps.sh" ]; then
        bash "$INSTALL_DIR/mcps/install-mcps.sh"
    else
        log_warn "MCP installer not found. MCPs will need manual configuration."
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
    echo -e "${CYAN}Next steps:${NC}"
    echo ""
    echo -e "  ${BLUE}1.${NC} Restart your shell or run:"
    echo -e "     ${YELLOW}source ~/.zshrc${NC}  (or ~/.bashrc)"
    echo ""
    echo -e "  ${BLUE}2.${NC} Set your OpenAI API key (for memory embeddings):"
    echo -e "     ${YELLOW}export OPENAI_API_KEY=\"sk-your-key-here\"${NC}"
    echo ""
    echo -e "  ${BLUE}3.${NC} Start infrastructure:"
    echo -e "     ${YELLOW}codeagent start${NC}"
    echo ""
    echo -e "  ${BLUE}4.${NC} Initialize in your project:"
    echo -e "     ${YELLOW}cd /your/project${NC}"
    echo -e "     ${YELLOW}codeagent init${NC}"
    echo ""
    echo -e "  ${BLUE}5.${NC} Start coding with Claude Code:"
    echo -e "     ${YELLOW}/scan${NC}              Build knowledge graph"
    echo -e "     ${YELLOW}/plan \"task\"${NC}       Research & design"
    echo -e "     ${YELLOW}/implement${NC}         TDD implementation"
    echo -e "     ${YELLOW}/review${NC}            Validate changes"
    echo ""
    echo -e "Documentation: ${CYAN}$INSTALL_DIR/Docs/${NC}"
    echo ""
}

# ============================================
# Main
# ============================================
main() {
    print_banner
    check_requirements
    install_codeagent
    configure_shell
    setup_global_config
    setup_api_keys
    install_mcps
    print_success
}

# Run
main "$@"
