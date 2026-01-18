#!/bin/bash

# Deployment script untuk Domainesia CloudHost
# Usage: ./deploy_domainesia.sh

set -e  # Exit on error

echo "======================================"
echo "Bank Soal SD - Deployment Script"
echo "======================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: File .env tidak ditemukan!"
    echo "Copy .env.production.example ke .env dan sesuaikan konfigurasi"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js tidak terinstall!"
    echo "Install Node.js terlebih dahulu"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 tidak terinstall!"
    exit 1
fi

echo "✓ Prerequisites check passed"
echo ""

# Step 1: Install Node dependencies
echo "[1/7] Installing Node.js dependencies..."
npm install
echo "✓ Node.js dependencies installed"
echo ""

# Step 2: Build CSS with Tailwind
echo "[2/7] Building CSS with Tailwind..."
npm run build
echo "✓ CSS built successfully"
echo ""

# Step 3: Copy flowbite source map
echo "[3/7] Copying flowbite source map..."
if [ -f "node_modules/flowbite/dist/flowbite.min.js.map" ]; then
    cp node_modules/flowbite/dist/flowbite.min.js.map static/js/
    echo "✓ Flowbite source map copied"
else
    echo "⚠ Warning: flowbite.min.js.map not found in node_modules"
fi
echo ""

# Step 4: Activate virtual environment
echo "[4/7] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 5: Install Python dependencies
echo "[5/7] Installing Python dependencies..."
pip install -r requirements/production.txt
echo "✓ Python dependencies installed"
echo ""

# Step 6: Run migrations
echo "[6/7] Running database migrations..."
python manage.py migrate --settings=config.settings.production
echo "✓ Migrations completed"
echo ""

# Step 7: Collect static files
echo "[7/7] Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production
echo "✓ Static files collected"
echo ""

echo "======================================"
echo "Deployment completed successfully! ✓"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Create superuser: python manage.py createsuperuser --settings=config.settings.production"
echo "2. Restart web server (touch tmp/restart.txt for Passenger)"
echo ""
