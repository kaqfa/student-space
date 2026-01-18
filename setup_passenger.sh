#!/bin/bash

# ============================================
# Setup Script untuk exp.fahrifirdaus.my.id
# ============================================
# Setup untuk struktur:
# - Source code: /home/fahrifir/student-space (dari GitHub)
# - Document root: /home/fahrifir/exp.fahrifirdaus.my.id (cPanel)
# - Virtual env: /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12

set -e

echo "============================================"
echo "Setup Passenger untuk exp.fahrifirdaus.my.id"
echo "============================================"
echo ""

# Paths
SOURCE_DIR="/home/fahrifir/student-space"          # Django source code (dari GitHub)
DOMAIN_DIR="/home/fahrifir/exp.fahrifirdaus.my.id"  # Document root (cPanel)
VENV_DIR="/home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12"

echo "Structure:"
echo "  Source code: $SOURCE_DIR (Django app dari GitHub)"
echo "  Document root: $DOMAIN_DIR (passenger_wsgi.py, .htaccess)"
echo "  Virtual env: $VENV_DIR"
echo ""

# ============================================
# 1. Copy passenger_wsgi.py ke DOCUMENT ROOT
# ============================================
echo "[1/6] Setting up passenger_wsgi.py..."
if [ ! -f "$SOURCE_DIR/passenger_wsgi.py" ]; then
    echo "  ERROR: passenger_wsgi.py tidak ditemukan di $SOURCE_DIR"
    echo "  Pastikan Anda sudah git pull di $SOURCE_DIR"
    exit 1
fi

echo "  Copying passenger_wsgi.py to $DOMAIN_DIR"
cp "$SOURCE_DIR/passenger_wsgi.py" "$DOMAIN_DIR/"
chmod 644 "$DOMAIN_DIR/passenger_wsgi.py"
echo "  ✓ Done"
echo ""

# ============================================
# 2. Copy .htaccess ke DOCUMENT ROOT
# ============================================
echo "[2/6] Setting up .htaccess..."
if [ ! -f "$SOURCE_DIR/.htaccess" ]; then
    echo "  Warning: .htaccess tidak ditemukan di $SOURCE_DIR"
    echo "  Menggunakan .htaccess yang sudah ada (jika ada)"
else
    if [ -f "$DOMAIN_DIR/.htaccess" ]; then
        echo "  ! .htaccess already exists"
        echo "  Creating backup: .htaccess.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$DOMAIN_DIR/.htaccess" "$DOMAIN_DIR/.htaccess.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    echo "  Copying .htaccess to $DOMAIN_DIR"
    cp "$SOURCE_DIR/.htaccess" "$DOMAIN_DIR/"
    chmod 644 "$DOMAIN_DIR/.htaccess"
    echo "  ✓ Done"
fi
echo ""

# ============================================
# 3. Setup static files directory
# ============================================
echo "[3/6] Setting up static files directories..."
mkdir -p "$DOMAIN_DIR/staticfiles"
mkdir -p "$DOMAIN_DIR/media"
echo "  ✓ Created staticfiles and media directories"
echo ""

# ============================================
# 4. Update .env file untuk path yang benar
# ============================================
echo "[4/6] Checking .env configuration..."
if [ -f "$SOURCE_DIR/.env" ]; then
    echo "  Updating STATIC_ROOT and MEDIA_ROOT in .env..."
    
    # Backup .env
    cp "$SOURCE_DIR/.env" "$SOURCE_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update or add STATIC_ROOT and MEDIA_ROOT
    if grep -q "^STATIC_ROOT=" "$SOURCE_DIR/.env"; then
        sed -i.bak "s|^STATIC_ROOT=.*|STATIC_ROOT=$DOMAIN_DIR/staticfiles|" "$SOURCE_DIR/.env"
    else
        echo "STATIC_ROOT=$DOMAIN_DIR/staticfiles" >> "$SOURCE_DIR/.env"
    fi
    
    if grep -q "^MEDIA_ROOT=" "$SOURCE_DIR/.env"; then
        sed -i.bak "s|^MEDIA_ROOT=.*|MEDIA_ROOT=$DOMAIN_DIR/media|" "$SOURCE_DIR/.env"
    else
        echo "MEDIA_ROOT=$DOMAIN_DIR/media" >> "$SOURCE_DIR/.env"
    fi
    
    # Remove backup files
    rm -f "$SOURCE_DIR/.env.bak"
    
    echo "  ✓ Updated .env"
else
    echo "  ! .env not found in $SOURCE_DIR"
    echo "  Please create .env file first:"
    echo "    cd $SOURCE_DIR"
    echo "    cp .env.production.example .env"
    echo "    nano .env  # Edit dengan credentials Anda"
fi
echo ""

# ============================================
# 5. Collect static files
# ============================================
echo "[5/6] Collecting static files..."
cd "$SOURCE_DIR"

# Check if venv exists
if [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "  ERROR: Virtual environment not found at $VENV_DIR"
    echo "  Setup virtual environment dulu dari cPanel"
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo "  Running collectstatic..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "  ✓ Static files collected to $DOMAIN_DIR/staticfiles"
echo ""

# ============================================
# 6. Restart Passenger
# ============================================
echo "[6/6] Restarting Passenger..."
mkdir -p "$DOMAIN_DIR/tmp"
touch "$DOMAIN_DIR/tmp/restart.txt"
echo "  ✓ Passenger restart triggered"
echo ""

echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "File Locations:"
echo "  Django source → $SOURCE_DIR"
echo "  passenger_wsgi.py → $DOMAIN_DIR/passenger_wsgi.py"
echo "  .htaccess → $DOMAIN_DIR/.htaccess"
echo "  Static files → $DOMAIN_DIR/staticfiles"
echo "  Media files → $DOMAIN_DIR/media"
echo ""
echo "Next steps:"
echo "  1. Visit: https://exp.fahrifirdaus.my.id"
echo "  2. If error, check: $DOMAIN_DIR/passenger_error.log"
echo "  3. Or check: ~/logs/error_log"
echo ""
echo "To update app in the future:"
echo "  cd $SOURCE_DIR"
echo "  git pull origin main"
echo "  ./setup_passenger.sh"
echo ""
