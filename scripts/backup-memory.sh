#!/bin/bash
# ============================================
# CodeAgent Memory Backup
# Backup Letta and Qdrant data
# ============================================

set -e

INSTALL_DIR="${CODEAGENT_HOME:-$HOME/.codeagent}"
BACKUP_DIR="${1:-$HOME/.codeagent-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}CodeAgent Memory Backup${NC}"
echo "========================"
echo ""

# Create backup directory
mkdir -p "$BACKUP_PATH"
echo -e "${BLUE}Backup location:${NC} $BACKUP_PATH"
echo ""

# Backup Letta data
echo -e "${BLUE}Backing up Letta...${NC}"
docker cp codeagent-letta:/root/.letta "$BACKUP_PATH/letta" 2>/dev/null || {
    echo -e "${YELLOW}○${NC} Letta backup skipped (container may not be running)"
}
echo -e "${GREEN}✓${NC} Letta backed up"

# Backup Qdrant vectors
echo -e "${BLUE}Backing up Qdrant...${NC}"
docker cp codeagent-qdrant:/qdrant/storage "$BACKUP_PATH/qdrant" 2>/dev/null || {
    echo -e "${YELLOW}○${NC} Qdrant backup skipped (container may not be running)"
}
echo -e "${GREEN}✓${NC} Qdrant backed up"

# Create archive
echo ""
echo -e "${BLUE}Creating archive...${NC}"
cd "$BACKUP_DIR"
tar -czf "backup_$TIMESTAMP.tar.gz" "backup_$TIMESTAMP"
rm -rf "$BACKUP_PATH"

ARCHIVE_SIZE=$(du -h "backup_$TIMESTAMP.tar.gz" | cut -f1)

echo ""
echo -e "${GREEN}Backup complete!${NC}"
echo ""
echo "Archive: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
echo "Size: $ARCHIVE_SIZE"
echo ""
echo "To restore: codeagent restore $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
