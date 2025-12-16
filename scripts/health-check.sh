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
echo "Qdrant Stats:"

# Get Qdrant collections info
QDRANT_COLLECTIONS=$(curl -sf "http://localhost:6333/collections" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$QDRANT_COLLECTIONS" ]; then
    COLLECTION_COUNT=$(echo "$QDRANT_COLLECTIONS" | grep -o '"name"' | wc -l)
    echo -e "  Collections: $COLLECTION_COUNT"

    # Get vector count from each collection
    TOTAL_VECTORS=0
    for col in $(echo "$QDRANT_COLLECTIONS" | grep -o '"name":"[^"]*"' | cut -d'"' -f4); do
        COL_INFO=$(curl -sf "http://localhost:6333/collections/$col" 2>/dev/null)
        if [ -n "$COL_INFO" ]; then
            VECTORS=$(echo "$COL_INFO" | grep -o '"vectors_count":[0-9]*' | cut -d':' -f2 | head -1)
            if [ -n "$VECTORS" ]; then
                TOTAL_VECTORS=$((TOTAL_VECTORS + VECTORS))
                echo -e "  - $col: $VECTORS vectors"
            fi
        fi
    done
    echo -e "  Total vectors: $TOTAL_VECTORS"

    # Memory warning if over 500K vectors
    if [ "$TOTAL_VECTORS" -gt 500000 ]; then
        echo -e "  ${YELLOW}!${NC} High vector count - consider cleanup"
    fi
else
    echo -e "  ${YELLOW}○${NC} Could not retrieve Qdrant stats"
fi

echo ""
echo "Letta Stats:"

# Get Letta agents count (use -sL to follow redirects, trailing slash required)
LETTA_AGENTS=$(curl -sL "http://localhost:8283/v1/agents/" 2>/dev/null)
if [ $? -eq 0 ]; then
    # Count agents (handles empty array [] gracefully)
    AGENT_COUNT=$(echo "$LETTA_AGENTS" | grep -o '"id"' | wc -l)
    echo -e "  Agents: $AGENT_COUNT"

    # List agent names if any exist
    if [ "$AGENT_COUNT" -gt 0 ]; then
        for agent in $(echo "$LETTA_AGENTS" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | head -5); do
            echo -e "  - $agent"
        done
        if [ "$AGENT_COUNT" -gt 5 ]; then
            echo -e "  ... and $((AGENT_COUNT - 5)) more"
        fi
    fi
else
    echo -e "  ${YELLOW}○${NC} Could not retrieve Letta stats"
fi

echo ""

if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}All services healthy!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some services need attention.${NC}"
    exit 1
fi
