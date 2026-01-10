#!/bin/bash
# ============================================
# CodeAgent Memory Restore
# Restore A-MEM and Qdrant data from backup
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

# Restore A-MEM (local storage)
if [ -d "$TEMP_DIR/$BACKUP_DIR/amem" ]; then
    echo -e "${BLUE}Restoring A-MEM...${NC}"
    AMEM_DIR="$INSTALL_DIR/memory"
    rm -rf "$AMEM_DIR" 2>/dev/null || true
    mkdir -p "$AMEM_DIR"
    cp -r "$TEMP_DIR/$BACKUP_DIR/amem/"* "$AMEM_DIR/" 2>/dev/null || true
    MEM_COUNT=$(find "$AMEM_DIR" -name "*.json" 2>/dev/null | wc -l || echo "0")
    echo -e "${GREEN}✓${NC} A-MEM restored ($MEM_COUNT memories)"
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
