#!/bin/bash
# ============================================
# CodeAgent Memory Restore
# Restore Letta and Neo4j data from backup
# ============================================

set -e

INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
BACKUP_FILE="$1"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: No backup file specified${NC}"
    echo ""
    echo "Usage: codeagent restore <backup_file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -la ~/.codeagent-backups/*.tar.gz 2>/dev/null || echo "  No backups found"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}CodeAgent Memory Restore${NC}"
echo "========================="
echo ""
echo -e "${YELLOW}Warning: This will overwrite current memory data!${NC}"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Extract backup
echo -e "${BLUE}Extracting backup...${NC}"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
BACKUP_DIR=$(ls "$TEMP_DIR")

# Stop services
echo -e "${BLUE}Stopping services...${NC}"
cd "$INSTALL_DIR/infrastructure"
docker compose down

# Restore Neo4j
if [ -d "$TEMP_DIR/$BACKUP_DIR/neo4j" ]; then
    echo -e "${BLUE}Restoring Neo4j...${NC}"
    docker volume rm codeagent_neo4j_data 2>/dev/null || true
    docker volume create codeagent_neo4j_data
    docker run --rm -v codeagent_neo4j_data:/data -v "$TEMP_DIR/$BACKUP_DIR/neo4j:/backup" \
        alpine sh -c "cp -r /backup/* /data/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Neo4j restored"
elif [ -f "$TEMP_DIR/$BACKUP_DIR/neo4j_export.json" ]; then
    echo -e "${YELLOW}○${NC} Neo4j export file found - will import after start"
fi

# Restore Letta
if [ -d "$TEMP_DIR/$BACKUP_DIR/letta" ]; then
    echo -e "${BLUE}Restoring Letta...${NC}"
    docker volume rm codeagent_letta_data 2>/dev/null || true
    docker volume create codeagent_letta_data
    docker run --rm -v codeagent_letta_data:/root/.letta -v "$TEMP_DIR/$BACKUP_DIR/letta:/backup" \
        alpine sh -c "cp -r /backup/* /root/.letta/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Letta restored"
fi

# Restore Qdrant
if [ -d "$TEMP_DIR/$BACKUP_DIR/qdrant" ]; then
    echo -e "${BLUE}Restoring Qdrant...${NC}"
    docker volume rm codeagent_qdrant_data 2>/dev/null || true
    docker volume create codeagent_qdrant_data
    docker run --rm -v codeagent_qdrant_data:/qdrant/storage -v "$TEMP_DIR/$BACKUP_DIR/qdrant:/backup" \
        alpine sh -c "cp -r /backup/* /qdrant/storage/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Qdrant restored"
fi

# Restart services
echo ""
echo -e "${BLUE}Restarting services...${NC}"
docker compose up -d

echo ""
echo -e "${GREEN}Restore complete!${NC}"
echo ""
echo "Run 'codeagent status' to verify services."
