#!/bin/bash

# ============================================
# Passenger Debug Helper Script
# ============================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "============================================"
echo "🔍 Passenger Debugging Tool"
echo "============================================"
echo ""

# Check if services are running
if ! docker compose ps | grep -q "student-space-passenger"; then
    echo -e "${RED}❌ Services are not running${NC}"
    echo "   Run: docker compose up -d"
    exit 1
fi

while true; do
    echo ""
    echo "Select debugging option:"
    echo ""
    echo "  ${BLUE}Status & Monitoring${NC}"
    echo "    1) Passenger status"
    echo "    2) Memory statistics"
    echo "    3) Container stats (CPU, RAM)"
    echo "    4) Apache status"
    echo ""
    echo "  ${BLUE}Logs${NC}"
    echo "    5) Follow web logs"
    echo "    6) Apache error log"
    echo "    7) Apache access log"
    echo "    8) Passenger debug log"
    echo "    9) Application error log"
    echo ""
    echo "  ${BLUE}Testing${NC}"
    echo "   10) Test homepage (curl)"
    echo "   11) Test static files"
    echo "   12) Test admin page"
    echo "   13) Apache config test"
    echo ""
    echo "  ${BLUE}Control${NC}"
    echo "   14) Restart Passenger app"
    echo "   15) Restart Apache"
    echo "   16) Restart all services"
    echo "   17) Enable debug logging"
    echo ""
    echo "  ${BLUE}Shell Access${NC}"
    echo "   18) Enter container shell"
    echo "   19) Django shell"
    echo "   20) Database shell"
    echo ""
    echo "   ${RED}0) Exit${NC}"
    echo ""
    read -p "Choose option [0-20]: " choice

    case $choice in
        1)
            echo -e "\n${BLUE}Passenger Status:${NC}"
            docker compose exec web passenger-status
            ;;
        2)
            echo -e "\n${BLUE}Memory Statistics:${NC}"
            docker compose exec web passenger-memory-stats
            ;;
        3)
            echo -e "\n${BLUE}Container Stats (Ctrl+C to stop):${NC}"
            docker stats student-space-passenger
            ;;
        4)
            echo -e "\n${BLUE}Apache Status:${NC}"
            docker compose exec web apache2ctl -t
            docker compose exec web apache2ctl -S
            ;;
        5)
            echo -e "\n${BLUE}Following web logs (Ctrl+C to stop):${NC}"
            docker compose logs -f web
            ;;
        6)
            echo -e "\n${BLUE}Apache Error Log (Ctrl+C to stop):${NC}"
            docker compose exec web tail -f /var/log/apache2/student-space-error.log
            ;;
        7)
            echo -e "\n${BLUE}Apache Access Log (Ctrl+C to stop):${NC}"
            docker compose exec web tail -f /var/log/apache2/student-space-access.log
            ;;
        8)
            echo -e "\n${BLUE}Passenger Debug Log (Ctrl+C to stop):${NC}"
            docker compose exec web tail -f /var/log/apache2/passenger-debug.log
            ;;
        9)
            echo -e "\n${BLUE}Application Error Log:${NC}"
            docker compose exec web cat /var/www/student-space/logs/passenger_error.log 2>/dev/null || echo "No errors logged yet"
            ;;
        10)
            echo -e "\n${BLUE}Testing Homepage:${NC}"
            curl -I http://localhost:8080/
            echo ""
            curl -s http://localhost:8080/ | head -20
            ;;
        11)
            echo -e "\n${BLUE}Testing Static Files:${NC}"
            echo "Checking static directory..."
            docker compose exec web ls -la /var/www/student-space/staticfiles/ | head -10
            ;;
        12)
            echo -e "\n${BLUE}Testing Admin Page:${NC}"
            curl -I http://localhost:8080/admin/
            ;;
        13)
            echo -e "\n${BLUE}Apache Configuration Test:${NC}"
            docker compose exec web apache2ctl -t
            ;;
        14)
            echo -e "\n${BLUE}Restarting Passenger App:${NC}"
            docker compose exec web passenger-config restart-app /var/www/student-space
            echo -e "${GREEN}✅ App restarted${NC}"
            ;;
        15)
            echo -e "\n${BLUE}Restarting Apache:${NC}"
            docker compose exec web apache2ctl graceful
            echo -e "${GREEN}✅ Apache restarted${NC}"
            ;;
        16)
            echo -e "\n${BLUE}Restarting All Services:${NC}"
            docker compose restart
            echo -e "${GREEN}✅ Services restarted${NC}"
            ;;
        17)
            echo -e "\n${BLUE}Enabling Debug Logging:${NC}"
            docker compose exec web bash -c \
              "echo 'PassengerLogLevel 7' >> /etc/apache2/sites-available/student-space.conf"
            docker compose exec web apache2ctl graceful
            echo -e "${GREEN}✅ Debug logging enabled${NC}"
            echo "View logs with: docker compose exec web tail -f /var/log/apache2/passenger-debug.log"
            ;;
        18)
            echo -e "\n${BLUE}Entering container shell (type 'exit' to quit):${NC}"
            docker compose exec web bash
            ;;
        19)
            echo -e "\n${BLUE}Django Shell (type 'exit()' to quit):${NC}"
            docker compose exec web python manage.py shell
            ;;
        20)
            echo -e "\n${BLUE}Database Shell (type '\\q' to quit):${NC}"
            docker compose exec db psql -U student -d studentspace
            ;;
        0)
            echo -e "\n${GREEN}Goodbye!${NC}\n"
            exit 0
            ;;
        *)
            echo -e "\n${RED}Invalid option${NC}"
            ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done
