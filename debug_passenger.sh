#!/bin/bash

# ============================================
# Debug Script untuk Passenger Configuration
# ============================================
# Script ini membantu men-debug masalah Passenger di Domainesia
# Usage: ./debug_passenger.sh

set +e  # Don't exit on error

echo "============================================"
echo "Passenger Configuration Debug Tool"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# 1. Check Current Directory
# ============================================
echo "1. Checking current directory..."
CURRENT_DIR=$(pwd)
echo "   Current directory: $CURRENT_DIR"
echo ""

# ============================================
# 2. Check Critical Files
# ============================================
echo "2. Checking critical files..."

# Check passenger_wsgi.py
if [ -f "passenger_wsgi.py" ]; then
    echo -e "   ${GREEN}✓${NC} passenger_wsgi.py exists"
    ls -lh passenger_wsgi.py
else
    echo -e "   ${RED}✗${NC} passenger_wsgi.py NOT FOUND!"
    echo "   Create this file in project root (same directory as manage.py)"
fi

# Check manage.py
if [ -f "manage.py" ]; then
    echo -e "   ${GREEN}✓${NC} manage.py exists (correct directory)"
else
    echo -e "   ${RED}✗${NC} manage.py NOT FOUND!"
    echo "   You might be in the wrong directory"
fi

# Check .env
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✓${NC} .env exists"
else
    echo -e "   ${YELLOW}!${NC} .env not found (optional but recommended)"
fi

# Check .htaccess
if [ -f "../.htaccess" ] || [ -f ".htaccess" ]; then
    echo -e "   ${GREEN}✓${NC} .htaccess found"
else
    echo -e "   ${YELLOW}!${NC} .htaccess not found in public_html"
    echo "   This file should be in your public_html or document root"
fi

echo ""

# ============================================
# 3. Check Virtual Environment
# ============================================
echo "3. Checking virtual environment..."

if [ -d "venv" ]; then
    echo -e "   ${GREEN}✓${NC} venv directory exists"
    
    if [ -f "venv/bin/python" ]; then
        echo -e "   ${GREEN}✓${NC} Python in venv exists"
        VENV_PYTHON="$CURRENT_DIR/venv/bin/python"
        echo "   Python path: $VENV_PYTHON"
        
        # Check Python version
        PYTHON_VERSION=$($VENV_PYTHON --version 2>&1)
        echo "   Python version: $PYTHON_VERSION"
    else
        echo -e "   ${RED}✗${NC} venv/bin/python NOT FOUND"
    fi
else
    echo -e "   ${RED}✗${NC} venv directory NOT FOUND"
    echo "   Create it with: python3 -m venv venv"
fi

echo ""

# ============================================
# 4. Check Django Installation
# ============================================
echo "4. Checking Django installation..."

if [ -f "venv/bin/python" ]; then
    DJANGO_VERSION=$(venv/bin/python -c "import django; print(django.get_version())" 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✓${NC} Django is installed: $DJANGO_VERSION"
    else
        echo -e "   ${RED}✗${NC} Django NOT installed in venv"
        echo "   Install with: venv/bin/pip install -r requirements/production.txt"
    fi
else
    echo -e "   ${YELLOW}!${NC} Cannot check (venv not found)"
fi

echo ""

# ============================================
# 5. Test WSGI Import
# ============================================
echo "5. Testing WSGI application import..."

if [ -f "venv/bin/python" ] && [ -f "passenger_wsgi.py" ]; then
    echo "   Running: python passenger_wsgi.py"
    
    # Create test script
    cat > test_wsgi.py << 'EOF'
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    import passenger_wsgi
    print("✓ WSGI import successful")
    if hasattr(passenger_wsgi, 'application'):
        print("✓ application object exists")
    else:
        print("✗ application object NOT FOUND")
except Exception as e:
    print(f"✗ Error importing WSGI: {e}")
    import traceback
    traceback.print_exc()
EOF
    
    venv/bin/python test_wsgi.py
    rm test_wsgi.py
else
    echo -e "   ${YELLOW}!${NC} Cannot test (missing venv or passenger_wsgi.py)"
fi

echo ""

# ============================================
# 6. Check Static Files
# ============================================
echo "6. Checking static files..."

if [ -d "staticfiles" ]; then
    FILE_COUNT=$(find staticfiles -type f | wc -l)
    echo -e "   ${GREEN}✓${NC} staticfiles directory exists ($FILE_COUNT files)"
else
    echo -e "   ${YELLOW}!${NC} staticfiles directory not found"
    echo "   Run: python manage.py collectstatic --settings=config.settings.production"
fi

echo ""

# ============================================
# 7. Check Permissions
# ============================================
echo "7. Checking file permissions..."

if [ -f "passenger_wsgi.py" ]; then
    WSGI_PERM=$(stat -f "%Lp" passenger_wsgi.py 2>/dev/null || stat -c "%a" passenger_wsgi.py 2>/dev/null)
    echo "   passenger_wsgi.py: $WSGI_PERM (should be 644 or 755)"
fi

DIR_PERM=$(stat -f "%Lp" . 2>/dev/null || stat -c "%a" . 2>/dev/null)
echo "   project directory: $DIR_PERM (should be 755)"

echo ""

# ============================================
# 8. Generate Configuration Template
# ============================================
echo "8. Configuration paths for .htaccess and passenger_wsgi.py:"
echo ""
echo "   PROJECT_ROOT=$CURRENT_DIR"
echo "   VENV_PYTHON=$CURRENT_DIR/venv/bin/python"
echo ""
echo "   Use these paths in your .htaccess:"
echo "   PassengerAppRoot $CURRENT_DIR"
echo "   PassengerPython $CURRENT_DIR/venv/bin/python"
echo ""

# ============================================
# 9. Check Passenger Process
# ============================================
echo "9. Checking Passenger processes..."
ps aux | grep -i passenger | grep -v grep || echo "   No Passenger processes found (normal if not started yet)"
echo ""

# ============================================
# 10. Recommendations
# ============================================
echo "============================================"
echo "Recommendations:"
echo "============================================"

if [ ! -f "passenger_wsgi.py" ]; then
    echo -e "${RED}1. CREATE passenger_wsgi.py in $CURRENT_DIR${NC}"
fi

if [ ! -d "venv" ]; then
    echo -e "${RED}2. CREATE virtual environment: python3 -m venv venv${NC}"
fi

if [ ! -d "staticfiles" ]; then
    echo -e "${YELLOW}3. RUN collectstatic: python manage.py collectstatic --settings=config.settings.production${NC}"
fi

echo ""
echo "To restart Passenger:"
echo "  mkdir -p tmp"
echo "  touch tmp/restart.txt"
echo ""
echo "To view Passenger errors:"
echo "  Check ~/logs/error_log or passenger_error.log in project root"
echo ""
echo "============================================"
