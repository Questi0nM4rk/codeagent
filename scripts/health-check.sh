#!/bin/bash
# ============================================
# CodeAgent Health Check
# Verify all services are running correctly
# ============================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

all_healthy=true

check_http_service() {
    local name=$1
    local url=$2
    local timeout=${3:-5}

    if curl -s --max-time "$timeout" "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name ($url)"
        return 0
    else
        echo -e "${RED}✗${NC} $name ($url) - not responding"
        all_healthy=false
        return 1
    fi
}

check_container() {
    local name=$1
    local container=$2

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
        if [ "$health" = "healthy" ] || [ "$health" = "none" ]; then
            echo -e "${GREEN}✓${NC} $name container running"
            return 0
        else
            echo -e "${YELLOW}○${NC} $name container status: $health"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} $name container not running"
        all_healthy=false
        return 1
    fi
}

echo "Health Check"
echo "============"
echo ""

# Check containers
echo "Containers:"
check_container "Neo4j" "codeagent-neo4j"
check_container "Qdrant" "codeagent-qdrant"
check_container "Letta" "codeagent-letta"

echo ""
echo "Services:"
check_http_service "Neo4j Browser" "http://localhost:7474"
check_http_service "Qdrant API" "http://localhost:6333/healthz"
check_http_service "Letta API" "http://localhost:8283/v1/health/"

echo ""

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}All services healthy!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some services need attention.${NC}"
    exit 1
fi
