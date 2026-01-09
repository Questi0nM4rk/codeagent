#!/bin/bash
# ============================================
# CodeAgent Test Runner (Host Script)
# Usage: ./test.sh [scenario] [options]
# ============================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
    echo -e "${CYAN}CodeAgent Test Sandbox${NC}"
    echo ""
    echo "Usage: ./test.sh [scenario] [options]"
    echo ""
    echo -e "${BLUE}Scenarios:${NC}"
    echo "  all         Run all test scenarios (default)"
    echo "  source      Validate source code only (fast)"
    echo "  clean       Test clean installation"
    echo "  cli         Test CLI commands"
    echo "  config      Test config/keyring helpers"
    echo "  marketplace Test marketplace commands"
    echo "  upgrade     Test upgrade over existing"
    echo "  force       Test force reinstall"
    echo "  uninstall   Test uninstall script"
    echo ""
    echo -e "${BLUE}Test Modes:${NC}"
    echo "  --github    Test actual curl one-liner from GitHub (requires SSH keys)"
    echo "  --local     Test using local source files (default, no network needed)"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo "  --shell     Open interactive shell in container (with SSH keys)"
    echo "  --rebuild   Force rebuild Docker image"
    echo "  --verbose   Show verbose output"
    echo "  --help      Show this help"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  ./test.sh                    # Run all tests (local mode)"
    echo "  ./test.sh --github           # Test real GitHub install"
    echo "  ./test.sh source             # Quick lint check"
    echo "  ./test.sh clean --github     # Test GitHub install only"
    echo "  ./test.sh --shell            # Debug in container"
    echo ""
}

main() {
    local scenario="all"
    local shell_mode=false
    local rebuild=false
    local verbose=false
    local test_mode="local"  # default to local

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --shell|-s)
                shell_mode=true
                shift
                ;;
            --rebuild|-r)
                rebuild=true
                shift
                ;;
            --verbose|-v)
                verbose=true
                shift
                ;;
            --github)
                test_mode="github"
                shift
                ;;
            --local)
                test_mode="local"
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            all|source|clean|cli|config|marketplace|upgrade|force|uninstall)
                scenario="$1"
                shift
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done

    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              CodeAgent Test Sandbox                        ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Select service based on test mode
    local service="test-local"
    if [ "$test_mode" = "github" ]; then
        service="test"
        echo -e "${BLUE}[INFO]${NC} Test mode: ${YELLOW}github${NC} (curl one-liner, needs SSH keys)"

        # Check if SSH keys exist
        if [ ! -f "$HOME/.ssh/id_ed25519" ] && [ ! -f "$HOME/.ssh/id_rsa" ]; then
            echo -e "${RED}[ERROR]${NC} No SSH keys found in ~/.ssh/"
            echo -e "${YELLOW}GitHub test mode requires SSH keys for cloning${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}[INFO]${NC} Test mode: ${GREEN}local${NC} (--local flag, no network)"
    fi

    # Build image
    if [ "$rebuild" = true ]; then
        echo -e "${BLUE}[INFO]${NC} Rebuilding Docker image..."
        docker compose build --no-cache
    else
        echo -e "${BLUE}[INFO]${NC} Building Docker image (if needed)..."
        docker compose build
    fi

    # Run tests or shell
    if [ "$shell_mode" = true ]; then
        echo -e "${BLUE}[INFO]${NC} Opening interactive shell..."
        echo -e "${YELLOW}Tip: Source code is at /home/testuser/codeagent-source${NC}"
        echo ""
        docker compose run --rm shell
    else
        echo -e "${BLUE}[INFO]${NC} Running test scenario: $scenario"
        echo ""

        # Export variables for docker-compose
        export TEST_SCENARIO="$scenario"
        export VERBOSE="$verbose"

        # Run tests
        if docker compose run --rm "$service"; then
            echo ""
            echo -e "${GREEN}Tests completed successfully!${NC}"
            exit 0
        else
            echo ""
            echo -e "${RED}Some tests failed.${NC}"
            exit 1
        fi
    fi
}

main "$@"
