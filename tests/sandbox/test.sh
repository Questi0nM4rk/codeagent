#!/bin/bash
# ============================================
# CodeAgent Test Runner (Host Script)
# Uses Docker-in-Docker for full isolation
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
    echo -e "${CYAN}CodeAgent Test Sandbox (Docker-in-Docker)${NC}"
    echo ""
    echo "Usage: ./test.sh [scenario] [options]"
    echo ""
    echo -e "${BLUE}Scenarios:${NC}"
    echo "  all         Run all test scenarios (default)"
    echo "  source      Validate source code only (fast, no Docker)"
    echo "  install     Test full installation"
    echo "  mcp         Test MCP installation"
    echo "  infra       Test infrastructure startup/shutdown"
    echo "  cli         Test CLI commands"
    echo "  config      Test config operations"
    echo ""
    echo -e "${BLUE}Options:${NC}"
    echo "  --shell     Open interactive shell in container"
    echo "  --rebuild   Force rebuild Docker image"
    echo "  --clean     Clean up all test containers and volumes"
    echo "  --verbose   Show verbose output"
    echo "  --help      Show this help"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  ./test.sh                    # Run all tests"
    echo "  ./test.sh source             # Quick lint check (no Docker needed)"
    echo "  ./test.sh install            # Test installation only"
    echo "  ./test.sh --shell            # Debug in container"
    echo "  ./test.sh --clean            # Clean up test environment"
    echo ""
    echo -e "${BLUE}How it works:${NC}"
    echo "  - Uses Docker-in-Docker (dind) for complete isolation"
    echo "  - All containers created during tests run INSIDE dind"
    echo "  - Your host Docker is never touched"
    echo "  - ./test.sh --clean removes everything"
    echo ""
}

cleanup() {
    echo -e "${BLUE}[INFO]${NC} Cleaning up test environment..."
    docker compose down -v --remove-orphans 2>/dev/null || true
    docker volume rm codeagent-sandbox_dind-storage 2>/dev/null || true
    echo -e "${GREEN}[OK]${NC} Test environment cleaned up"
}

main() {
    local scenario="all"
    local shell_mode=false
    local rebuild=false
    local verbose=false
    local clean_mode=false

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
            --clean|-c)
                clean_mode=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            all|source|install|mcp|infra|cli|config)
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

    # Handle clean mode
    if [ "$clean_mode" = true ]; then
        cleanup
        exit 0
    fi

    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║         CodeAgent Test Sandbox (Docker-in-Docker)         ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check SSH keys for GitHub access
    if ! ls "$HOME/.ssh/"*[!.pub] >/dev/null 2>&1; then
        echo -e "${YELLOW}[WARN]${NC} No SSH keys found in ~/.ssh/"
        echo -e "${YELLOW}       GitHub clone may fail${NC}"
    fi

    # Source-only test doesn't need dind
    if [ "$scenario" = "source" ]; then
        echo -e "${BLUE}[INFO]${NC} Running source validation (no Docker-in-Docker needed)..."
        echo ""

        if [ "$rebuild" = true ]; then
            docker compose build --no-cache lint
        else
            docker compose build lint
        fi

        if docker compose run --rm lint; then
            echo ""
            echo -e "${GREEN}Source validation passed!${NC}"
            exit 0
        else
            echo ""
            echo -e "${RED}Source validation failed.${NC}"
            exit 1
        fi
    fi

    # Full tests need dind
    echo -e "${BLUE}[INFO]${NC} Test scenario: ${YELLOW}$scenario${NC}"
    echo -e "${BLUE}[INFO]${NC} Using Docker-in-Docker for full isolation"
    echo ""

    # Build image
    if [ "$rebuild" = true ]; then
        echo -e "${BLUE}[INFO]${NC} Rebuilding Docker image..."
        docker compose build --no-cache test
    else
        echo -e "${BLUE}[INFO]${NC} Building Docker image (if needed)..."
        docker compose build test
    fi

    # Run tests or shell
    if [ "$shell_mode" = true ]; then
        echo -e "${BLUE}[INFO]${NC} Starting dind and opening interactive shell..."
        echo -e "${YELLOW}Tip: Source code is at /home/testuser/codeagent-source${NC}"
        echo -e "${YELLOW}     Docker commands connect to dind (isolated)${NC}"
        echo ""
        docker compose run --rm shell
    else
        echo -e "${BLUE}[INFO]${NC} Starting Docker-in-Docker daemon..."

        # Export variables for docker-compose
        export TEST_SCENARIO="$scenario"
        export VERBOSE="$verbose"

        # Run tests (dind starts automatically via depends_on)
        if docker compose run --rm test; then
            echo ""
            echo -e "${GREEN}Tests completed successfully!${NC}"

            # Cleanup after successful test
            echo -e "${BLUE}[INFO]${NC} Cleaning up..."
            docker compose down -v --remove-orphans 2>/dev/null || true

            exit 0
        else
            echo ""
            echo -e "${RED}Some tests failed.${NC}"

            # Keep environment for debugging on failure
            echo -e "${YELLOW}[INFO]${NC} Test environment preserved for debugging"
            echo -e "${YELLOW}       Run ./test.sh --shell to investigate${NC}"
            echo -e "${YELLOW}       Run ./test.sh --clean when done${NC}"

            exit 1
        fi
    fi
}

main "$@"
