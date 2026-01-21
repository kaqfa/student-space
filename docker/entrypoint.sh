#!/bin/bash
set -e

echo ""
echo "============================================"
echo "🚀 Student Space - Passenger Docker Setup"
echo "============================================"
echo ""

# Activate virtualenv
export PATH="/var/www/venv/bin:$PATH"
cd /var/www/student-space

# ============================================
# 1. Wait for Database
# ============================================
echo "📊 Waiting for database connection..."
RETRIES=30
until nc -z ${DB_HOST:-db} ${DB_PORT:-5432} || [ $RETRIES -eq 0 ]; do
  echo "  ⏳ Waiting for database... ($RETRIES attempts remaining)"
  RETRIES=$((RETRIES-1))
  sleep 2
done

if [ $RETRIES -eq 0 ]; then
  echo "  ❌ Could not connect to database!"
  echo "  Database host: ${DB_HOST:-db}:${DB_PORT:-5432}"
  exit 1
fi

echo "  ✅ Database is ready!"
echo ""

# ============================================
# 2. Run Database Migrations
# ============================================
echo "📦 Running database migrations..."
python manage.py migrate --noinput || {
  echo "  ❌ Migration failed!"
  echo "  Check database connection and settings"
  exit 1
}
echo "  ✅ Migrations completed successfully"
echo ""

# ============================================
# 3. Collect Static Files
# ============================================
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || {
  echo "  ⚠️  Static files collection failed (non-critical)"
}
echo "  ✅ Static files collected"
echo ""

# ============================================
# 4. Create Superuser (if not exists)
# ============================================
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "👤 Setting up superuser..."
  python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = '${DJANGO_SUPERUSER_USERNAME:-admin}'
email = '${DJANGO_SUPERUSER_EMAIL:-admin@localhost}'
password = '${DJANGO_SUPERUSER_PASSWORD:-admin123}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'  ✅ Superuser created: {username}')
    print(f'     Email: {email}')
    print(f'     Password: {password}')
else:
    print(f'  ℹ️  Superuser already exists: {username}')
EOF
  echo ""
fi

# ============================================
# 5. Create Required Directories
# ============================================
echo "📂 Setting up directories..."
mkdir -p /var/www/student-space/public
mkdir -p /var/www/student-space/staticfiles
mkdir -p /var/www/student-space/media
mkdir -p /var/www/student-space/logs
echo "  ✅ Directories created"
echo ""

# ============================================
# 6. Set Permissions
# ============================================
echo "🔐 Setting permissions..."
chown -R app:app /var/www/student-space
chmod -R 755 /var/www/student-space
chmod -R 775 /var/www/student-space/media
chmod -R 775 /var/www/student-space/logs
echo "  ✅ Permissions set"
echo ""

# ============================================
# 7. Display Configuration
# ============================================
echo "============================================"
echo "📋 Configuration Summary"
echo "============================================"
echo "Python version: $(python --version)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"
echo "Settings module: ${DJANGO_SETTINGS_MODULE:-config.settings.production}"
echo "Debug mode: ${DEBUG:-False}"
echo "Database: ${DB_ENGINE:-postgresql}"
echo "Database host: ${DB_HOST:-db}:${DB_PORT:-5432}"
echo "Allowed hosts: ${ALLOWED_HOSTS:-*}"
echo "============================================"
echo ""

# ============================================
# 8. Test Django Configuration
# ============================================
echo "🧪 Testing Django configuration..."
python manage.py check --deploy || {
  echo "  ⚠️  Django check found some issues (see above)"
  echo "  Continuing anyway..."
}
echo ""

# ============================================
# 9. Display Access Information
# ============================================
echo "============================================"
echo "✅ Setup Complete!"
echo "============================================"
echo ""
echo "🌐 Access your application:"
echo "   Web:        http://localhost:8080"
echo "   Admin:      http://localhost:8080/admin"
echo ""
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "👤 Superuser credentials:"
  echo "   Username:   ${DJANGO_SUPERUSER_USERNAME:-admin}"
  echo "   Password:   ${DJANGO_SUPERUSER_PASSWORD:-admin123}"
  echo ""
fi
echo "🔧 Useful commands:"
echo "   Status:     docker-compose exec web passenger-status"
echo "   Memory:     docker-compose exec web passenger-memory-stats"
echo "   Logs:       docker-compose logs -f web"
echo "   Shell:      docker-compose exec web bash"
echo "   Apache:     docker-compose exec web apache2ctl -t"
echo ""
echo "🚀 Starting Passenger + Apache..."
echo "============================================"
echo ""

# ============================================
# 10. Enable Apache runit service
# ============================================
# The phusion/passenger image uses runit for service management
# Apache is already configured as a service, we just need to ensure it starts
mkdir -p /etc/service/apache2
if [ ! -f /etc/service/apache2/run ]; then
  cat > /etc/service/apache2/run << 'RUNIT'
#!/bin/sh
exec /usr/sbin/apache2ctl -D FOREGROUND
RUNIT
  chmod +x /etc/service/apache2/run
fi

# ============================================
# 11. Start Services
# ============================================
# Execute the baseimage-docker init system
# This will start all runit services including Apache with Passenger
exec /sbin/my_init
