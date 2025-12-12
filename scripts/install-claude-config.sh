#!/bin/bash
# ============================================
# Claude Code Configuration Installer
# Handles skills, commands, hooks, settings, CLAUDE.md
# ============================================

set -e

# Colors (inherit from parent or define)
RED=${RED:-'\033[0;31m'}
GREEN=${GREEN:-'\033[0;32m'}
YELLOW=${YELLOW:-'\033[1;33m'}
BLUE=${BLUE:-'\033[0;34m'}
CYAN=${CYAN:-'\033[0;36m'}
NC=${NC:-'\033[0m'}

# Configuration
FORCE=${CODEAGENT_FORCE:-false}
INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
CLAUDE_DIR="$HOME/.claude"
SOURCE_DIR="$INSTALL_DIR/framework"
TEMPLATES_DIR="$INSTALL_DIR/templates"
REGISTRY_FILE="$INSTALL_DIR/config-registry.json"

# ============================================
# Logging Functions
# ============================================
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============================================
# Validation Functions
# ============================================

# Validate a skill directory
validate_skill() {
    local skill_dir=$1
    local skill_name=$(basename "$skill_dir")
    local errors=()

    # Check directory exists
    if [ ! -d "$skill_dir" ]; then
        errors+=("Skill must be a directory")
    fi

    # Check SKILL.md exists
    if [ ! -f "$skill_dir/SKILL.md" ]; then
        errors+=("Missing SKILL.md")
        echo "${errors[*]}"
        return 1
    fi

    # Extract frontmatter (between first two ---)
    local frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_dir/SKILL.md" | sed '1d;$d')

    # Check YAML is valid (use grep for basic validation if yq not available)
    if command -v yq &> /dev/null; then
        if ! echo "$frontmatter" | yq . > /dev/null 2>&1; then
            errors+=("Invalid YAML frontmatter")
        fi

        # Check required fields
        local name=$(echo "$frontmatter" | yq -r '.name' 2>/dev/null)
        local desc=$(echo "$frontmatter" | yq -r '.description' 2>/dev/null)

        if [ -z "$name" ] || [ "$name" = "null" ]; then
            errors+=("Missing required field: name")
        fi

        if [ -z "$desc" ] || [ "$desc" = "null" ]; then
            errors+=("Missing required field: description")
        fi

        # Check name matches directory
        if [ "$name" != "$skill_name" ]; then
            errors+=("Name mismatch: $name vs $skill_name")
        fi

        # Check description length
        if [ ${#desc} -gt 1024 ]; then
            errors+=("Description too long (max 1024 chars)")
        fi
    else
        # Basic validation without yq
        if ! grep -q "^name:" <<< "$frontmatter"; then
            errors+=("Missing required field: name")
        fi
        if ! grep -q "^description:" <<< "$frontmatter"; then
            errors+=("Missing required field: description")
        fi
    fi

    if [ ${#errors[@]} -gt 0 ]; then
        echo "${errors[*]}"
        return 1
    fi

    return 0
}

# Validate a command file
validate_command() {
    local cmd_file=$1
    local errors=()

    # Check file exists
    if [ ! -f "$cmd_file" ]; then
        errors+=("Command file not found")
        echo "${errors[*]}"
        return 1
    fi

    # Extract frontmatter
    local frontmatter=$(sed -n '/^---$/,/^---$/p' "$cmd_file" | sed '1d;$d')

    # Check YAML is valid
    if command -v yq &> /dev/null; then
        if ! echo "$frontmatter" | yq . > /dev/null 2>&1; then
            errors+=("Invalid YAML frontmatter")
        fi

        # Check description exists
        local desc=$(echo "$frontmatter" | yq -r '.description' 2>/dev/null)
        if [ -z "$desc" ] || [ "$desc" = "null" ]; then
            errors+=("Missing required field: description")
        fi
    else
        # Basic validation without yq
        if ! grep -q "^description:" <<< "$frontmatter"; then
            errors+=("Missing required field: description")
        fi
    fi

    if [ ${#errors[@]} -gt 0 ]; then
        echo "${errors[*]}"
        return 1
    fi

    return 0
}

# Validate a hook script
validate_hook() {
    local hook_file=$1
    local errors=()

    # Check file exists
    if [ ! -f "$hook_file" ]; then
        errors+=("Hook file not found")
        echo "${errors[*]}"
        return 1
    fi

    # Check is executable
    if [ ! -x "$hook_file" ]; then
        errors+=("Hook not executable")
    fi

    # Check bash syntax
    if ! bash -n "$hook_file" 2>/dev/null; then
        errors+=("Invalid bash syntax")
    fi

    if [ ${#errors[@]} -gt 0 ]; then
        echo "${errors[*]}"
        return 1
    fi

    return 0
}

# Validate settings.json
validate_settings() {
    local settings_file=$1
    local errors=()

    # Check file exists
    if [ ! -f "$settings_file" ]; then
        errors+=("Settings file not found")
        echo "${errors[*]}"
        return 1
    fi

    # Check JSON is valid
    if ! jq . "$settings_file" > /dev/null 2>&1; then
        errors+=("Invalid JSON")
        echo "${errors[*]}"
        return 1
    fi

    # Check required structure
    if ! jq -e '.permissions' "$settings_file" > /dev/null 2>&1; then
        errors+=("Missing permissions section")
    fi

    if [ ${#errors[@]} -gt 0 ]; then
        echo "${errors[*]}"
        return 1
    fi

    return 0
}

# ============================================
# Pre-flight Checks
# ============================================
check_claude_cli() {
    if ! command -v claude &> /dev/null; then
        log_warn "Claude Code CLI not found"
        log_info "Install from: https://claude.ai/code"
        log_info "Continuing installation anyway..."
    else
        log_success "Claude Code CLI found"
    fi
}

check_existing_state() {
    local has_config=false

    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        has_config=true
        EXISTING_CLAUDE_MD=true
    fi

    if [ -f "$CLAUDE_DIR/settings.json" ]; then
        has_config=true
        EXISTING_SETTINGS=true
    fi

    if [ -d "$CLAUDE_DIR/skills" ] && [ "$(ls -A $CLAUDE_DIR/skills 2>/dev/null)" ]; then
        has_config=true
        EXISTING_SKILLS=$(ls -d "$CLAUDE_DIR/skills"/*/ 2>/dev/null | wc -l)
    fi

    if [ -d "$CLAUDE_DIR/commands" ] && [ "$(ls -A $CLAUDE_DIR/commands/*.md 2>/dev/null)" ]; then
        has_config=true
        EXISTING_COMMANDS=$(ls "$CLAUDE_DIR/commands"/*.md 2>/dev/null | wc -l)
    fi

    if [ -d "$CLAUDE_DIR/hooks" ] && [ "$(ls -A $CLAUDE_DIR/hooks/*.sh 2>/dev/null)" ]; then
        has_config=true
        EXISTING_HOOKS=$(ls "$CLAUDE_DIR/hooks"/*.sh 2>/dev/null | wc -l)
    fi

    HAS_EXISTING_CONFIG=$has_config
}

# ============================================
# Backup Functions
# ============================================
create_backup() {
    local backup_dir="$HOME/.claude-backup-$(date +%Y%m%d_%H%M%S)"

    log_info "Creating backup at $backup_dir..."
    mkdir -p "$backup_dir"

    # Copy existing configs
    [ -f "$CLAUDE_DIR/CLAUDE.md" ] && cp "$CLAUDE_DIR/CLAUDE.md" "$backup_dir/"
    [ -f "$CLAUDE_DIR/settings.json" ] && cp "$CLAUDE_DIR/settings.json" "$backup_dir/"
    [ -d "$CLAUDE_DIR/skills" ] && cp -r "$CLAUDE_DIR/skills" "$backup_dir/"
    [ -d "$CLAUDE_DIR/commands" ] && cp -r "$CLAUDE_DIR/commands" "$backup_dir/"
    [ -d "$CLAUDE_DIR/hooks" ] && cp -r "$CLAUDE_DIR/hooks" "$backup_dir/"

    log_success "Backup created: $backup_dir"
    BACKUP_DIR="$backup_dir"
}

# ============================================
# Installation Functions
# ============================================

# Install all skills from registry
install_skills() {
    log_info "Installing skills..."

    mkdir -p "$CLAUDE_DIR/skills"

    local installed=0
    local skipped=0
    local failed=0

    # Read skills from registry
    if [ -f "$REGISTRY_FILE" ]; then
        local skill_count=$(jq '.skills | length' "$REGISTRY_FILE")

        for ((i=0; i<skill_count; i++)); do
            local skill_name=$(jq -r ".skills[$i].name" "$REGISTRY_FILE")
            local skill_source=$(jq -r ".skills[$i].source" "$REGISTRY_FILE")
            local source_path="$INSTALL_DIR/$skill_source"
            local target_path="$CLAUDE_DIR/skills/$skill_name"

            # Check if already exists and not force
            if [ -d "$target_path" ] && [ "$FORCE" != "true" ]; then
                # Compare files
                if diff -q "$source_path/SKILL.md" "$target_path/SKILL.md" > /dev/null 2>&1; then
                    ((skipped++)) || true
                    continue
                fi
            fi

            # Copy skill directory
            mkdir -p "$target_path"
            cp -r "$source_path"/* "$target_path/" 2>/dev/null || {
                log_error "Failed to copy skill: $skill_name"
                ((failed++)) || true
                continue
            }

            # Validate after install
            if ! validate_skill "$target_path" > /dev/null 2>&1; then
                log_error "Skill validation failed: $skill_name"
                ((failed++)) || true
                continue
            fi

            ((installed++)) || true
        done
    else
        # Fallback: install from directory structure
        for skill_dir in "$SOURCE_DIR/skills"/*/; do
            if [ -d "$skill_dir" ]; then
                local skill_name=$(basename "$skill_dir")
                local target_path="$CLAUDE_DIR/skills/$skill_name"

                if [ -d "$target_path" ] && [ "$FORCE" != "true" ]; then
                    if diff -q "$skill_dir/SKILL.md" "$target_path/SKILL.md" > /dev/null 2>&1; then
                        ((skipped++)) || true
                        continue
                    fi
                fi

                mkdir -p "$target_path"
                cp -r "$skill_dir"* "$target_path/" 2>/dev/null || {
                    log_error "Failed to copy skill: $skill_name"
                    ((failed++)) || true
                    continue
                }

                if ! validate_skill "$target_path" > /dev/null 2>&1; then
                    log_error "Skill validation failed: $skill_name"
                    ((failed++)) || true
                    continue
                fi

                ((installed++)) || true
            fi
        done
    fi

    if [ $installed -gt 0 ]; then
        log_success "Installed $installed skills"
    fi
    if [ $skipped -gt 0 ]; then
        log_info "Skipped $skipped unchanged skills"
    fi
    if [ $failed -gt 0 ]; then
        log_warn "Failed to install $failed skills"
    fi
}

# Install all commands from registry
install_commands() {
    log_info "Installing commands..."

    mkdir -p "$CLAUDE_DIR/commands"

    local installed=0
    local skipped=0
    local failed=0

    if [ -f "$REGISTRY_FILE" ]; then
        local cmd_count=$(jq '.commands | length' "$REGISTRY_FILE")

        for ((i=0; i<cmd_count; i++)); do
            local cmd_name=$(jq -r ".commands[$i].name" "$REGISTRY_FILE")
            local cmd_source=$(jq -r ".commands[$i].source" "$REGISTRY_FILE")
            local source_path="$INSTALL_DIR/$cmd_source"
            local target_path="$CLAUDE_DIR/commands/$cmd_name.md"

            if [ -f "$target_path" ] && [ "$FORCE" != "true" ]; then
                if diff -q "$source_path" "$target_path" > /dev/null 2>&1; then
                    ((skipped++)) || true
                    continue
                fi
            fi

            cp "$source_path" "$target_path" 2>/dev/null || {
                log_error "Failed to copy command: $cmd_name"
                ((failed++)) || true
                continue
            }

            if ! validate_command "$target_path" > /dev/null 2>&1; then
                log_error "Command validation failed: $cmd_name"
                ((failed++)) || true
                continue
            fi

            ((installed++)) || true
        done
    else
        # Fallback: install from directory
        for cmd_file in "$SOURCE_DIR/commands"/*.md; do
            if [ -f "$cmd_file" ]; then
                local cmd_name=$(basename "$cmd_file" .md)
                local target_path="$CLAUDE_DIR/commands/$cmd_name.md"

                if [ -f "$target_path" ] && [ "$FORCE" != "true" ]; then
                    if diff -q "$cmd_file" "$target_path" > /dev/null 2>&1; then
                        ((skipped++)) || true
                        continue
                    fi
                fi

                cp "$cmd_file" "$target_path" 2>/dev/null || {
                    log_error "Failed to copy command: $cmd_name"
                    ((failed++)) || true
                    continue
                }

                if ! validate_command "$target_path" > /dev/null 2>&1; then
                    log_error "Command validation failed: $cmd_name"
                    ((failed++)) || true
                    continue
                fi

                ((installed++)) || true
            fi
        done
    fi

    if [ $installed -gt 0 ]; then
        log_success "Installed $installed commands"
    fi
    if [ $skipped -gt 0 ]; then
        log_info "Skipped $skipped unchanged commands"
    fi
    if [ $failed -gt 0 ]; then
        log_warn "Failed to install $failed commands"
    fi
}

# Install all hooks from registry
install_hooks() {
    log_info "Installing hooks..."

    mkdir -p "$CLAUDE_DIR/hooks"

    local installed=0
    local skipped=0
    local failed=0

    if [ -f "$REGISTRY_FILE" ]; then
        local hook_count=$(jq '.hooks | length' "$REGISTRY_FILE")

        for ((i=0; i<hook_count; i++)); do
            local hook_name=$(jq -r ".hooks[$i].name" "$REGISTRY_FILE")
            local hook_source=$(jq -r ".hooks[$i].source" "$REGISTRY_FILE")
            local source_path="$INSTALL_DIR/$hook_source"
            local target_path="$CLAUDE_DIR/hooks/$hook_name.sh"

            if [ -f "$target_path" ] && [ "$FORCE" != "true" ]; then
                if diff -q "$source_path" "$target_path" > /dev/null 2>&1; then
                    ((skipped++)) || true
                    continue
                fi
            fi

            cp "$source_path" "$target_path" 2>/dev/null || {
                log_error "Failed to copy hook: $hook_name"
                ((failed++)) || true
                continue
            }

            chmod +x "$target_path"

            if ! validate_hook "$target_path" > /dev/null 2>&1; then
                log_error "Hook validation failed: $hook_name"
                ((failed++)) || true
                continue
            fi

            ((installed++)) || true
        done
    else
        # Fallback: install from directory
        for hook_file in "$SOURCE_DIR/hooks"/*.sh; do
            if [ -f "$hook_file" ]; then
                local hook_name=$(basename "$hook_file" .sh)
                local target_path="$CLAUDE_DIR/hooks/$hook_name.sh"

                if [ -f "$target_path" ] && [ "$FORCE" != "true" ]; then
                    if diff -q "$hook_file" "$target_path" > /dev/null 2>&1; then
                        ((skipped++)) || true
                        continue
                    fi
                fi

                cp "$hook_file" "$target_path" 2>/dev/null || {
                    log_error "Failed to copy hook: $hook_name"
                    ((failed++)) || true
                    continue
                }

                chmod +x "$target_path"

                if ! validate_hook "$target_path" > /dev/null 2>&1; then
                    log_error "Hook validation failed: $hook_name"
                    ((failed++)) || true
                    continue
                fi

                ((installed++)) || true
            fi
        done
    fi

    if [ $installed -gt 0 ]; then
        log_success "Installed $installed hooks"
    fi
    if [ $skipped -gt 0 ]; then
        log_info "Skipped $skipped unchanged hooks"
    fi
    if [ $failed -gt 0 ]; then
        log_warn "Failed to install $failed hooks"
    fi
}

# Install settings.json
install_settings() {
    log_info "Installing settings.json..."

    local source_file="$SOURCE_DIR/settings.json.template"
    local target_file="$CLAUDE_DIR/settings.json"

    if [ ! -f "$source_file" ]; then
        log_error "Settings template not found: $source_file"
        return 1
    fi

    if [ "$INSTALL_MODE" = "fresh" ] || [ "$FORCE" = "true" ]; then
        # Fresh install: copy template directly
        cp "$source_file" "$target_file"
        log_success "Installed settings.json from template"
    elif [ "$INSTALL_MODE" = "merge" ]; then
        # Merge: combine existing with template
        merge_settings "$source_file" "$target_file"
    else
        # Skip
        log_info "Skipping settings.json installation"
        return 0
    fi

    # Validate
    if ! validate_settings "$target_file" > /dev/null 2>&1; then
        log_error "Settings validation failed"
        return 1
    fi

    log_success "Settings validated"
}

# Merge settings.json
merge_settings() {
    local source_file=$1
    local target_file=$2

    if [ ! -f "$target_file" ]; then
        cp "$source_file" "$target_file"
        return 0
    fi

    log_info "Merging settings..."

    # Create merged file using jq
    local merged=$(mktemp)

    # Merge permissions.allow arrays (deduplicate)
    jq -s '
        .[0] as $existing |
        .[1] as $new |
        {
            permissions: {
                allow: (($existing.permissions.allow // []) + ($new.permissions.allow // []) | unique),
                deny: (($existing.permissions.deny // []) + ($new.permissions.deny // []) | unique)
            },
            hooks: ($new.hooks // $existing.hooks // {}),
            env: (($existing.env // {}) * ($new.env // {})),
            mcpServers: (($existing.mcpServers // {}) * ($new.mcpServers // {}))
        }
    ' "$target_file" "$source_file" > "$merged"

    if [ -s "$merged" ]; then
        mv "$merged" "$target_file"
        log_success "Merged settings.json"
    else
        log_error "Failed to merge settings"
        rm -f "$merged"
        return 1
    fi
}

# Install CLAUDE.md
install_claude_md() {
    log_info "Installing CLAUDE.md..."

    local source_file="$TEMPLATES_DIR/CLAUDE.md.template"
    local target_file="$CLAUDE_DIR/CLAUDE.md"

    if [ "$INSTALL_MODE" = "skip" ]; then
        log_info "Skipping CLAUDE.md installation"
        return 0
    fi

    if [ "$FORCE" = "true" ]; then
        # Force: completely replace with our template
        if [ -f "$source_file" ]; then
            cp "$source_file" "$target_file"
            log_success "Replaced CLAUDE.md with CodeAgent template"
        else
            log_error "CLAUDE.md template not found: $source_file"
            return 1
        fi
        return 0
    fi

    # Non-force: create if missing, or append section if exists
    if [ ! -f "$target_file" ]; then
        if [ -f "$source_file" ]; then
            cp "$source_file" "$target_file"
            log_success "Created CLAUDE.md from template"
        else
            log_warn "CLAUDE.md template not found, skipping"
        fi
    else
        # Exists - only append CodeAgent section if missing
        if ! grep -q "CodeAgent Integration" "$target_file"; then
            echo "" >> "$target_file"
            echo "## CodeAgent Integration" >> "$target_file"
            echo "This configuration works with CodeAgent." >> "$target_file"
            echo 'Run `codeagent init` in your project to set up project-specific agents and commands.' >> "$target_file"
            log_success "Added CodeAgent section to existing CLAUDE.md"
        else
            log_info "CodeAgent section already present in CLAUDE.md"
        fi
    fi
}

# ============================================
# Clean ALL Claude Configs (for --force)
# ============================================
clean_all_configs() {
    log_warn "Wiping ALL existing Claude Code configurations..."

    # Remove everything in ~/.claude/
    rm -rf "$CLAUDE_DIR/skills" 2>/dev/null
    rm -rf "$CLAUDE_DIR/commands" 2>/dev/null
    rm -rf "$CLAUDE_DIR/hooks" 2>/dev/null
    rm -rf "$CLAUDE_DIR/rules" 2>/dev/null
    rm -f "$CLAUDE_DIR/settings.json" 2>/dev/null
    rm -f "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null

    log_success "Wiped all Claude Code configurations"
}

# ============================================
# User Prompt
# ============================================
prompt_user_choice() {
    echo ""
    echo -e "${YELLOW}Existing Claude Code configuration detected:${NC}"
    [ "$EXISTING_CLAUDE_MD" = true ] && echo "  - ~/.claude/CLAUDE.md"
    [ "$EXISTING_SETTINGS" = true ] && echo "  - ~/.claude/settings.json"
    [ -n "$EXISTING_SKILLS" ] && echo "  - ~/.claude/skills/ ($EXISTING_SKILLS skills)"
    [ -n "$EXISTING_COMMANDS" ] && echo "  - ~/.claude/commands/ ($EXISTING_COMMANDS commands)"
    [ -n "$EXISTING_HOOKS" ] && echo "  - ~/.claude/hooks/ ($EXISTING_HOOKS hooks)"
    echo ""
    echo "Options:"
    echo "  1) Backup existing and install CodeAgent config (recommended)"
    echo "  2) Merge (keep existing, add CodeAgent additions)"
    echo "  3) Skip (don't modify existing config)"
    echo ""
    read -p "Choose option [1/2/3]: " -n 1 -r config_choice
    echo ""

    case "$config_choice" in
        1)
            INSTALL_MODE="fresh"
            create_backup
            ;;
        2)
            INSTALL_MODE="merge"
            ;;
        3)
            INSTALL_MODE="skip"
            ;;
        *)
            log_warn "Invalid choice, defaulting to skip"
            INSTALL_MODE="skip"
            ;;
    esac
}

# ============================================
# Verification
# ============================================
verify_all_configs() {
    echo ""
    log_info "Verifying installed configurations..."

    local all_ok=true

    # Verify skills
    local skill_count=0
    local skill_errors=0
    for skill_dir in "$CLAUDE_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            ((skill_count++)) || true
            if ! validate_skill "$skill_dir" > /dev/null 2>&1; then
                log_error "Invalid skill: $(basename "$skill_dir")"
                ((skill_errors++)) || true
                all_ok=false
            fi
        fi
    done
    log_info "Skills: $skill_count installed, $skill_errors errors"

    # Verify commands
    local cmd_count=0
    local cmd_errors=0
    for cmd_file in "$CLAUDE_DIR/commands"/*.md; do
        if [ -f "$cmd_file" ]; then
            ((cmd_count++)) || true
            if ! validate_command "$cmd_file" > /dev/null 2>&1; then
                log_error "Invalid command: $(basename "$cmd_file")"
                ((cmd_errors++)) || true
                all_ok=false
            fi
        fi
    done
    log_info "Commands: $cmd_count installed, $cmd_errors errors"

    # Verify hooks
    local hook_count=0
    local hook_errors=0
    for hook_file in "$CLAUDE_DIR/hooks"/*.sh; do
        if [ -f "$hook_file" ]; then
            ((hook_count++)) || true
            if ! validate_hook "$hook_file" > /dev/null 2>&1; then
                log_error "Invalid hook: $(basename "$hook_file")"
                ((hook_errors++)) || true
                all_ok=false
            fi
        fi
    done
    log_info "Hooks: $hook_count installed, $hook_errors errors"

    # Verify settings
    if [ -f "$CLAUDE_DIR/settings.json" ]; then
        if ! validate_settings "$CLAUDE_DIR/settings.json" > /dev/null 2>&1; then
            log_error "Invalid settings.json"
            all_ok=false
        else
            log_success "Settings.json valid"
        fi
    fi

    # Verify CLAUDE.md
    if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
        log_success "CLAUDE.md present"
    fi

    echo ""
    if [ "$all_ok" = true ]; then
        log_success "All configurations verified successfully!"
    else
        log_warn "Some configurations have issues - check errors above"
    fi

    return 0
}

# ============================================
# Report Summary
# ============================================
report_summary() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║           Claude Code Configuration Summary                    ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo -e "  ${BLUE}Skills:${NC}    $(ls -d "$CLAUDE_DIR/skills"/*/ 2>/dev/null | wc -l)"
    echo -e "  ${BLUE}Commands:${NC}  $(ls "$CLAUDE_DIR/commands"/*.md 2>/dev/null | wc -l)"
    echo -e "  ${BLUE}Hooks:${NC}     $(ls "$CLAUDE_DIR/hooks"/*.sh 2>/dev/null | wc -l)"
    echo -e "  ${BLUE}Settings:${NC}  $([ -f "$CLAUDE_DIR/settings.json" ] && echo "Yes" || echo "No")"
    echo -e "  ${BLUE}CLAUDE.md:${NC} $([ -f "$CLAUDE_DIR/CLAUDE.md" ] && echo "Yes" || echo "No")"

    if [ -n "$BACKUP_DIR" ]; then
        echo ""
        echo -e "  ${YELLOW}Backup:${NC}    $BACKUP_DIR"
    fi

    echo ""
}

# ============================================
# Main Entry Point
# ============================================
main() {
    echo ""
    log_info "Installing Claude Code configurations..."
    echo ""

    # Phase 1: Pre-flight checks
    check_claude_cli
    check_existing_state

    # Phase 2-3: Handle existing configs
    if [ "$HAS_EXISTING_CONFIG" = true ]; then
        if [ "$FORCE" = "true" ]; then
            log_warn "Force mode: backing up and WIPING ALL existing configs..."
            create_backup
            clean_all_configs
            INSTALL_MODE="fresh"
        else
            prompt_user_choice
        fi
    else
        INSTALL_MODE="fresh"
    fi

    # Exit if user chose to skip
    if [ "$INSTALL_MODE" = "skip" ]; then
        log_info "Skipping Claude Code configuration"
        return 0
    fi

    # Create base directory
    mkdir -p "$CLAUDE_DIR"

    # Phase 4-6: Install components
    install_skills
    install_commands
    install_hooks

    # Phase 7-8: Install settings and memory
    install_settings
    install_claude_md

    # Phase 9: Verify
    verify_all_configs

    # Report
    report_summary
}

# Run main
main "$@"
