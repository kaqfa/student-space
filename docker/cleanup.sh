#!/bin/bash

# ============================================
# Docker Cleanup Script
# Remove all Student Space Docker resources
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "============================================"
echo "🧹 Docker Cleanup for Student Space"
echo "============================================"
echo ""

echo -e "${YELLOW}⚠️  WARNING: This will remove:${NC}"
echo "   - All running containers"
echo "   - All Docker volumes (database data will be lost)"
echo "   - All Docker images"
echo "   - All networks"
echo ""

read -p "Are you sure you want to continue? [y/N]: " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}Cleanup cancelled${NC}\n"
    exit 0
fi

echo ""
echo -e "${BLUE}Starting cleanup...${NC}"
echo ""

# Stop and remove containers
echo -e "${BLUE}1. Stopping and removing containers...${NC}"
docker compose down 2>/dev/null || echo "   No containers to remove"

# Remove volumes
echo -e "${BLUE}2. Removing volumes...${NC}"
docker compose down -v 2>/dev/null || echo "   No volumes to remove"

# Remove images
echo -e "${BLUE}3. Removing images...${NC}"
docker rmi $(docker images | grep student-space | awk '{print $3}') 2>/dev/null || echo "   No images to remove"

# Remove networks
echo -e "${BLUE}4. Removing networks...${NC}"
docker network rm student-space-network 2>/dev/null || echo "   No networks to remove"

# Clean up Docker system (optional)
echo ""
read -p "Do you want to clean up unused Docker resources system-wide? [y/N]: " cleanup_system

if [[ $cleanup_system =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}5. Cleaning up Docker system...${NC}"
    docker system prune -f
    echo ""
    read -p "Also remove unused volumes system-wide? [y/N]: " cleanup_volumes
    if [[ $cleanup_volumes =~ ^[Yy]$ ]]; then
        docker volume prune -f
    fi
fi

echo ""
echo "============================================"
echo -e "${GREEN}✅ Cleanup completed!${NC}"
echo "============================================"
echo ""
echo "To rebuild from scratch:"
echo "  ./docker/quick-start.sh"
echo ""
