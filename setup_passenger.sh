#!/bin/bash

# ============================================
# Setup Script untuk exp.fahrifirdaus.my.id
# ============================================

set -e

echo "============================================"
echo "Setup Passenger untuk exp.fahrifirdaus.my.id"
echo "============================================"
echo ""

# Paths
APP_DIR="/home/fahrifir/student-space"
DOMAIN_DIR="/home/fahrifir/exp.fahrifirdaus.my.id"
VENV_DIR="/home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12"

echo "Checking directories..."
echo "  App directory: $APP_DIR"
echo "  Domain directory: $DOMAIN_DIR"
echo "  Virtual env: $VENV_DIR"
echo ""

# ============================================
# 1. Copy passenger_wsgi.py ke app directory
# ============================================
echo "[1/5] Setting up passenger_wsgi.py..."
if [ -f "$APP_DIR/passenger_wsgi.py" ]; then
    echo "  ✓ passenger_wsgi.py already exists in $APP_DIR"
else
    echo "  Copying passenger_wsgi.py to $APP_DIR"
    cp passenger_wsgi.py "$APP_DIR/"
    chmod 644 "$APP_DIR/passenger_wsgi.py"
    echo "  ✓ Done"
fi
echo ""

# ============================================
# 2. Copy .htaccess ke domain directory
# ============================================
echo "[2/5] Setting up .htaccess..."
if [ -f "$DOMAIN_DIR/.htaccess" ]; then
    echo "  ! .htaccess already exists"
    echo "  Creating backup: .htaccess.backup"
    cp "$DOMAIN_DIR/.htaccess" "$DOMAIN_DIR/.htaccess.backup"
fi
echo "  Copying .htaccess to $DOMAIN_DIR"
cp .htaccess "$DOMAIN_DIR/"
chmod 644 "$DOMAIN_DIR/.htaccess"
echo "  ✓ Done"
echo ""

# ============================================
# 3. Setup static files directory
# ============================================
echo "[3/5] Setting up static files..."
mkdir -p "$DOMAIN_DIR/staticfiles"
mkdir -p "$DOMAIN_DIR/media"
echo "  ✓ Created staticfiles and media directories"
echo ""

# ============================================
# 4. Update .env file untuk path yang benar
# ============================================
echo "[4/5] Checking .env configuration..."
if [ -f "$APP_DIR/.env" ]; then
    echo "  Updating STATIC_ROOT and MEDIA_ROOT in .env..."
    
    # Backup .env
    cp "$APP_DIR/.env" "$APP_DIR/.env.backup"
    
    # Update paths (jika belum ada, tambahkan)
    if grep -q "STATIC_ROOT=" "$APP_DIR/.env"; then
        sed -i.bak "s|STATIC_ROOT=.*|STATIC_ROOT=$DOMAIN_DIR/staticfiles|" "$APP_DIR/.env"
    else
        echo "STATIC_ROOT=$DOMAIN_DIR/staticfiles" >> "$APP_DIR/.env"
    fi
    
    if grep -q "MEDIA_ROOT=" "$APP_DIR/.env"; then
        sed -i.bak "s|MEDIA_ROOT=.*|MEDIA_ROOT=$DOMAIN_DIR/media|" "$APP_DIR/.env"
    else
        echo "MEDIA_ROOT=$DOMAIN_DIR/media" >> "$APP_DIR/.env"
    fi
    
    echo "  ✓ Updated .env"
else
    echo "  ! .env not found in $APP_DIR"
    echo "  Please create .env file first"
fi
echo ""

# ============================================
# 5. Collect static files
# ============================================
echo "[5/5] Collecting static files..."
cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

echo "  Running collectstatic..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "  ✓ Static files collected"
echo ""

# ============================================
# 6. Restart Passenger
# ============================================
echo "Restarting Passenger..."
mkdir -p "$APP_DIR/tmp"
touch "$APP_DIR/tmp/restart.txt"
echo "  ✓ Passenger restart triggered"
echo ""

echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Configuration Summary:"
echo "  passenger_wsgi.py → $APP_DIR/passenger_wsgi.py"
echo "  .htaccess → $DOMAIN_DIR/.htaccess"
echo "  Static files → $DOMAIN_DIR/staticfiles"
echo "  Media files → $DOMAIN_DIR/media"
echo ""
echo "Next steps:"
echo "  1. Visit: https://exp.fahrifirdaus.my.id"
echo "  2. If error, check: $APP_DIR/passenger_error.log"
echo "  3. Or check: ~/logs/error_log"
echo ""
