#!/bin/bash
# Deployment helper script for Bank Soal SD

set -e  # Exit on error

echo "🚀 Bank Soal SD - Production Deployment"
echo "========================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please create .env from .env.production.example"
    exit 1
fi

# Check DJANGO_SETTINGS_MODULE
if ! grep -q "DJANGO_SETTINGS_MODULE=config.settings.production" .env; then
    echo "⚠️  Warning: DJANGO_SETTINGS_MODULE may not be set to production"
fi

echo "✅ Environment file found"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements/production.txt

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run deployment checks
echo ""
echo "🔍 Running deployment checks..."
python manage.py check --deploy

echo ""
echo "✅ Deployment preparation complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Review any warnings from deployment check"
echo "  2. Create superuser: python manage.py createsuperuser"
echo "  3. Start gunicorn: gunicorn config.wsgi:application"
echo ""
