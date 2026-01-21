# Docker Passenger Testing

Quick reference untuk testing Student Space dengan Passenger di lokal.

## 🚀 Quick Start

```bash
# Jalankan quick start script
./docker/quick-start.sh

# Atau manual:
docker compose build
docker compose up -d
```

## 📱 Access

- **Web**: http://localhost:8080
- **Admin**: http://localhost:8080/admin (admin/admin123)
- **pgAdmin**: http://localhost:8081

## 🔧 Useful Commands

```bash
# Status
docker compose ps
docker compose exec web passenger-status
docker compose exec web passenger-memory-stats

# Logs
docker compose logs -f web
docker compose exec web tail -f /var/log/apache2/student-space-error.log

# Debug
./docker/debug-passenger.sh

# Shell
docker compose exec web bash
docker compose exec web python manage.py shell

# Restart
docker compose restart web
docker compose exec web passenger-config restart-app /var/www/student-space

# Stop
docker compose down
docker compose down -v  # Also remove volumes
```

## 📖 Full Documentation

Lihat [DOCKER_PASSENGER_TESTING.md](../DOCKER_PASSENGER_TESTING.md) untuk dokumentasi lengkap.

## 📁 Files

- `Dockerfile` - Apache + Passenger image
- `apache-config.conf` - Apache VirtualHost configuration
- `passenger_wsgi.py` - WSGI entry point
- `entrypoint.sh` - Container startup script
- `quick-start.sh` - Quick start helper
- `debug-passenger.sh` - Debugging tool

## 🎯 Testing Checklist

- [ ] Build berhasil
- [ ] Container start tanpa error
- [ ] Homepage accessible (http://localhost:8080)
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Database connection works
- [ ] Migrations applied
- [ ] No errors in logs

## 🐛 Troubleshooting

**Container won't start:**
```bash
docker compose logs web
docker compose down -v
docker compose build --no-cache
```

**Static files not loading:**
```bash
docker compose exec web python manage.py collectstatic --noinput --clear
```

**Database connection error:**
```bash
docker compose down
docker compose up -d
```

**View detailed logs:**
```bash
./docker/debug-passenger.sh  # Choose option 5-9
```
