# Docker Passenger Testing Environment

Dokumentasi lengkap untuk testing Student Space dengan Passenger di lokal menggunakan Docker sebelum deploy ke Domainesia.

## 📋 Daftar Isi

- [Pendahuluan](#pendahuluan)
- [Struktur Project](#struktur-project)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Konfigurasi](#konfigurasi)
- [Testing](#testing)
- [Debugging](#debugging)
- [Production Simulation](#production-simulation)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Pendahuluan

Setup Docker ini mensimulasikan environment **Domainesia cPanel + Passenger + Apache** di lokal. Tujuannya:

✅ **Testing sebelum deploy** - Pastikan aplikasi berjalan dengan Passenger
✅ **Debugging errors** - Identifikasi masalah sebelum ke production
✅ **Performance testing** - Test performa dengan Passenger
✅ **Configuration validation** - Validasi konfigurasi Apache & Passenger

### Simulasi Environment Domainesia

| Component | Production (Domainesia) | Docker (Local) |
|-----------|------------------------|----------------|
| Web Server | Apache + Passenger | Apache + Passenger |
| Python | 3.12 | 3.12 |
| Database | PostgreSQL 12 | PostgreSQL 12 |
| WSGI | passenger_wsgi.py | passenger_wsgi.py |
| Structure | cPanel directories | Simulated paths |

---

## 📁 Struktur Project

```
student-space/
├── docker/
│   ├── Dockerfile              # Passenger + Apache image
│   ├── apache-config.conf      # Apache VirtualHost config
│   ├── passenger_wsgi.py       # WSGI entry point
│   └── entrypoint.sh           # Container startup script
├── docker-compose.yml          # Services orchestration
├── .env.docker                 # Environment variables
└── DOCKER_PASSENGER_TESTING.md # Dokumentasi ini
```

---

## ⚙️ Prerequisites

### System Requirements

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Memory**: Minimum 2GB RAM available
- **Disk**: Minimum 5GB free space

### Installation

**Ubuntu/Debian:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**macOS:**
```bash
# Install via Homebrew
brew install --cask docker
```

**Windows:**
- Download [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Verify Installation

```bash
docker --version
docker compose version
```

---

## 🚀 Quick Start

### 1. Build Docker Image

```bash
# Build image pertama kali (займет 5-10 menit)
docker compose build

# Build dengan no-cache jika ada masalah
docker compose build --no-cache
```

### 2. Start Services

```bash
# Start semua services (web, database, pgadmin)
docker compose up -d

# Follow logs
docker compose logs -f web
```

### 3. Access Application

Tunggu ~30-60 detik untuk startup, kemudian akses:

- **Application**: http://localhost:8080
- **Admin Panel**: http://localhost:8080/admin
- **pgAdmin**: http://localhost:8081

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

### 4. Stop Services

```bash
# Stop services
docker compose down

# Stop dan hapus volumes (reset database)
docker compose down -v
```

---

## 🔧 Konfigurasi

### Environment Variables (.env.docker)

Edit `.env.docker` untuk mengubah konfigurasi:

```bash
# Debug mode (set False untuk production simulation)
DEBUG=False

# Database
DB_NAME=studentspace
DB_USER=student
DB_PASSWORD=student123

# Superuser
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=admin123
```

### Apache Configuration

Edit `docker/apache-config.conf` untuk tuning:

```apache
# Passenger tuning
PassengerMaxPoolSize 6          # Jumlah worker processes
PassengerMinInstances 1         # Minimum instances running
PassengerMaxRequests 1000       # Recycle after N requests
PassengerLogLevel 3             # Log verbosity (1-7)
```

### Passenger WSGI

File `docker/passenger_wsgi.py` adalah replica dari production:

- Activate virtualenv
- Load environment variables
- Set Django settings module
- Error logging

---

## 🧪 Testing

### Basic Functionality Tests

```bash
# Test homepage
curl http://localhost:8080

# Test static files
curl http://localhost:8080/static/css/style.css

# Test admin (should redirect to login)
curl -I http://localhost:8080/admin/

# Test health
docker compose exec web curl -f http://localhost/
```

### Passenger Status & Monitoring

```bash
# Check Passenger status
docker compose exec web passenger-status

# Expected output:
# Version : 6.x.x
# Date    : ...
# Instance: ...
# ----------- General information -----------
# Max pool size : 6
# Processes     : 2
# ...

# Memory statistics
docker compose exec web passenger-memory-stats

# Restart application
docker compose exec web passenger-config restart-app /var/www/student-space
```

### Apache Tests

```bash
# Test Apache configuration syntax
docker compose exec web apache2ctl -t

# View Apache modules
docker compose exec web apache2ctl -M | grep passenger

# Server status
curl http://localhost:8080/server-status

# Passenger status page
curl http://localhost:8080/passenger-status
```

### Database Tests

```bash
# Connect to PostgreSQL
docker compose exec db psql -U student -d studentspace

# Run Django database commands
docker compose exec web python manage.py dbshell

# Check migrations
docker compose exec web python manage.py showmigrations
```

### Performance Tests

```bash
# Apache Bench - 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:8080/

# Siege - load testing
siege -c 10 -t 30s http://localhost:8080/
```

---

## 🐛 Debugging

### View Logs

```bash
# All services
docker compose logs -f

# Web server only
docker compose logs -f web

# Database only
docker compose logs -f db

# Last 100 lines
docker compose logs --tail=100 web

# Apache error log
docker compose exec web tail -f /var/log/apache2/student-space-error.log

# Apache access log
docker compose exec web tail -f /var/log/apache2/student-space-access.log

# Passenger debug log
docker compose exec web tail -f /var/log/apache2/passenger-debug.log

# Application logs
docker compose exec web tail -f /var/www/student-space/logs/passenger_error.log
```

### Enter Container

```bash
# Get shell access
docker compose exec web bash

# Inside container:
cd /var/www/student-space
source /var/www/venv/bin/activate
python manage.py shell

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check Django settings
python manage.py diffsettings
```

### Enable Debug Mode

```bash
# Edit .env.docker
DEBUG=True

# Restart services
docker compose restart web

# Or set temporarily:
docker compose exec web bash -c "export DEBUG=True && python manage.py runserver 0.0.0.0:8000"
```

### Enable Passenger Debug Logging

```bash
# Set log level to maximum (7)
docker compose exec web bash -c \
  "echo 'PassengerLogLevel 7' >> /etc/apache2/sites-available/student-space.conf"

# Graceful reload
docker compose exec web apache2ctl graceful

# View debug logs
docker compose exec web tail -f /var/log/apache2/passenger-debug.log
```

### Check Environment Variables

```bash
# Inside Passenger process
docker compose exec web passenger-config restart-app --debug /var/www/student-space

# Check loaded env vars
docker compose exec web python manage.py shell -c \
  "import os; print('\n'.join(f'{k}={v}' for k,v in os.environ.items() if 'DB' in k or 'DJANGO' in k))"
```

---

## 🎯 Production Simulation

### Strict Production Mode

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    environment:
      - PASSENGER_APP_ENV=production
      - DEBUG=False
      - SECURE_SSL_REDIRECT=True
      - SESSION_COOKIE_SECURE=True
      - CSRF_COOKIE_SECURE=True
    env_file:
      - .env.production.docker
```

Run with:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Production Checklist

Before deploying to Domainesia, verify:

- [ ] `DEBUG=False` works without errors
- [ ] Static files served correctly
- [ ] Media uploads work
- [ ] Database migrations applied
- [ ] Admin panel accessible
- [ ] No errors in Passenger logs
- [ ] Performance acceptable (test with `ab` or `siege`)
- [ ] Memory usage acceptable (`passenger-memory-stats`)
- [ ] All environment variables loaded correctly

### Deployment Testing Workflow

```bash
# 1. Build fresh image
docker compose build --no-cache

# 2. Start with production settings
DEBUG=False docker compose up -d

# 3. Run migrations
docker compose exec web python manage.py migrate

# 4. Collect static
docker compose exec web python manage.py collectstatic --noinput

# 5. Run tests
docker compose exec web python manage.py test

# 6. Check deployment
docker compose exec web python manage.py check --deploy

# 7. Load test
ab -n 1000 -c 10 http://localhost:8080/

# 8. Monitor
docker compose exec web passenger-status
docker compose exec web passenger-memory-stats

# 9. Check logs for errors
docker compose logs web | grep -i error
```

---

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check container status
docker compose ps

# Check logs
docker compose logs web

# Common fixes:
# 1. Port already in use
sudo lsof -i :8080
docker compose down

# 2. Build issues
docker compose build --no-cache

# 3. Volume permissions
docker compose down -v
docker volume prune
```

### Database Connection Failed

```bash
# Check database container
docker compose ps db

# Test connection
docker compose exec db pg_isready -U student

# View database logs
docker compose logs db

# Reset database
docker compose down -v
docker compose up -d
```

### Static Files Not Loading

```bash
# Collect static files again
docker compose exec web python manage.py collectstatic --noinput --clear

# Check permissions
docker compose exec web ls -la /var/www/student-space/staticfiles

# Check Apache config
docker compose exec web grep -A 5 "Alias /static" /etc/apache2/sites-available/student-space.conf
```

### Passenger Not Starting

```bash
# Check Passenger installation
docker compose exec web passenger-config --version

# Check Apache modules
docker compose exec web apache2ctl -M | grep passenger

# Restart Apache
docker compose exec web apache2ctl restart

# Check Passenger logs
docker compose exec web tail -f /var/log/apache2/passenger-debug.log
```

### Application Errors

```bash
# Check WSGI file
docker compose exec web python docker/passenger_wsgi.py

# Check Django settings
docker compose exec web python manage.py check

# Test WSGI directly
docker compose exec web python -c "
import sys
sys.path.insert(0, '/var/www/student-space')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
print('WSGI OK')
"
```

### Memory Issues

```bash
# Check container memory
docker stats student-space-passenger

# Reduce Passenger pool size in apache-config.conf:
PassengerMaxPoolSize 3  # Default: 6

# Restart
docker compose restart web
```

### Slow Performance

```bash
# Enable Passenger caching
PassengerHighPerformance on

# Increase workers (if you have RAM)
PassengerMaxPoolSize 10

# Check memory usage
docker compose exec web passenger-memory-stats

# Profile requests
docker compose exec web tail -f /var/log/apache2/student-space-access.log
```

---

## 📊 Useful Commands Reference

### Docker Compose

```bash
# Build
docker compose build                    # Build images
docker compose build --no-cache        # Build from scratch

# Start/Stop
docker compose up -d                   # Start in background
docker compose down                    # Stop services
docker compose down -v                 # Stop and remove volumes
docker compose restart                 # Restart all services
docker compose restart web             # Restart web only

# Logs
docker compose logs -f                 # Follow all logs
docker compose logs -f web             # Follow web logs
docker compose logs --tail=100 web     # Last 100 lines

# Status
docker compose ps                      # List services
docker compose top                     # Show running processes

# Execute commands
docker compose exec web bash           # Get shell
docker compose exec web python manage.py shell
docker compose exec db psql -U student -d studentspace
```

### Passenger

```bash
# Status & monitoring
docker compose exec web passenger-status
docker compose exec web passenger-memory-stats
docker compose exec web passenger-config about

# Restart
docker compose exec web passenger-config restart-app /var/www/student-space
docker compose exec web touch /var/www/student-space/tmp/restart.txt

# Debug
docker compose exec web passenger-config restart-app --debug /var/www/student-space
```

### Apache

```bash
# Configuration
docker compose exec web apache2ctl -t           # Test config
docker compose exec web apache2ctl -S           # Show vhosts
docker compose exec web apache2ctl -M           # Show modules

# Control
docker compose exec web apache2ctl restart
docker compose exec web apache2ctl graceful
docker compose exec web apache2ctl stop
```

### Django

```bash
# Management commands
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic
docker compose exec web python manage.py check --deploy
docker compose exec web python manage.py shell
docker compose exec web python manage.py dbshell
docker compose exec web python manage.py showmigrations
```

---

## 🎓 Best Practices

1. **Always test with `DEBUG=False`** before deploying
2. **Monitor logs** during first run
3. **Run `check --deploy`** to catch security issues
4. **Test static files** serving
5. **Verify database** connections
6. **Load test** with realistic traffic
7. **Check memory usage** with passenger-memory-stats
8. **Document** any custom configurations

---

## 📚 Resources

- [Passenger Documentation](https://www.phusionpassenger.com/docs/)
- [Apache Documentation](https://httpd.apache.org/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Domainesia Deployment Guide](DEPLOYMENT_DOMAINESIA.md)

---

## 🆘 Support

Jika menemui masalah:

1. Check logs: `docker compose logs -f web`
2. Check [Troubleshooting](#troubleshooting) section
3. Check Passenger logs: `docker compose exec web tail -f /var/log/apache2/passenger-debug.log`
4. Search [Passenger community](https://groups.google.com/g/phusion-passenger)

---

**Happy Testing! 🚀**
