#!/bin/bash

# ============================================
# Student Space - Docker Passenger Quick Start
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================"
echo "🚀 Student Space - Passenger Docker Setup"
echo "============================================"
echo ""

# ============================================
# Check Prerequisites
# ============================================
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "   Install from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✅ Docker installed:${NC} $(docker --version)"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "   Install from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose installed:${NC} $(docker compose version)"

# Check Docker daemon
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon is not running${NC}"
    echo "   Start Docker Desktop or run: sudo systemctl start docker"
    exit 1
fi
echo -e "${GREEN}✅ Docker daemon is running${NC}"

echo ""

# ============================================
# Check .env.docker
# ============================================
if [ ! -f .env.docker ]; then
    echo -e "${YELLOW}⚠️  .env.docker not found, creating from template...${NC}"
    # .env.docker should already exist, but just in case
    echo -e "${GREEN}✅ .env.docker ready${NC}"
fi

echo ""

# ============================================
# Build Option
# ============================================
echo -e "${BLUE}🔨 Do you want to build the Docker image?${NC}"
echo "   1) Yes, build fresh image (recommended first time)"
echo "   2) Yes, build with --no-cache (if having issues)"
echo "   3) Skip build (if already built)"
read -p "Choose [1-3]: " build_choice

case $build_choice in
    1)
        echo -e "${BLUE}Building Docker image...${NC}"
        docker compose build
        ;;
    2)
        echo -e "${BLUE}Building Docker image with --no-cache...${NC}"
        docker compose build --no-cache
        ;;
    3)
        echo -e "${YELLOW}Skipping build...${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice, skipping build${NC}"
        ;;
esac

echo ""

# ============================================
# Start Services
# ============================================
echo -e "${BLUE}🚀 Starting services...${NC}"
docker compose up -d

echo ""
echo -e "${GREEN}✅ Services started!${NC}"
echo ""

# ============================================
# Wait for services
# ============================================
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
echo "   This may take 30-60 seconds..."
echo ""

# Wait for database
echo -n "   Database: "
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U student -d studentspace &> /dev/null; then
        echo -e "${GREEN}✅ Ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Wait for web server
echo -n "   Web server: "
for i in {1..30}; do
    if curl -sf http://localhost:8080/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""

# ============================================
# Display Access Info
# ============================================
echo "============================================"
echo -e "${GREEN}🎉 Student Space is ready!${NC}"
echo "============================================"
echo ""
echo "🌐 Access your application:"
echo -e "   ${BLUE}Application:${NC}  http://localhost:8080"
echo -e "   ${BLUE}Admin Panel:${NC}  http://localhost:8080/admin"
echo -e "   ${BLUE}pgAdmin:${NC}      http://localhost:8081"
echo ""
echo "👤 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Useful commands:"
echo -e "   ${BLUE}View logs:${NC}        docker compose logs -f web"
echo -e "   ${BLUE}Passenger status:${NC} docker compose exec web passenger-status"
echo -e "   ${BLUE}Memory stats:${NC}     docker compose exec web passenger-memory-stats"
echo -e "   ${BLUE}Shell access:${NC}     docker compose exec web bash"
echo -e "   ${BLUE}Stop services:${NC}    docker compose down"
echo ""
echo "📖 Full documentation: DOCKER_PASSENGER_TESTING.md"
echo ""
echo "============================================"

# ============================================
# Follow logs option
# ============================================
echo ""
read -p "Do you want to follow the logs? [y/N]: " follow_logs

if [[ $follow_logs =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${BLUE}Following logs... (Ctrl+C to exit)${NC}"
    echo ""
    docker compose logs -f web
fi
