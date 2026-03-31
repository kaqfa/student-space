# Docker Passenger Testing

Quick reference untuk testing Student Space dengan Passenger di lokal.

## 🚀 Quick Start

```bash
# Siapkan env dan jalankan
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build
```

## 📱 Access

- **Web**: http://localhost:8080
- **Admin**: http://localhost:8080/admin (admin / admin123)
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

# Restart Passenger (tanpa rebuild)
docker compose exec web passenger-config restart-app /var/www/student-space

# Stop
docker compose down
docker compose down -v  # Also remove volumes
```

## 📁 Files

- `Dockerfile` — Apache + Passenger image (di root project)
- `deploy/apache/student-space.conf` — Apache VirtualHost configuration
- `deploy/scripts/docker-entrypoint.sh` — Container startup script
- `passenger_wsgi.py` — WSGI entry point (di root project, berlaku untuk Docker & Domainesia)
- `docker/quick-start.sh` — Quick start helper
- `docker/debug-passenger.sh` — Debugging tool

## 🎯 Testing Checklist

- [ ] Build berhasil
- [ ] Container start tanpa error
- [ ] Homepage accessible (http://localhost:8080)
- [ ] Admin panel accessible
- [ ] Static files loading
- [ ] Database connection ke PostgreSQL (bukan SQLite)
- [ ] Migrations applied
- [ ] No errors in logs

## 🐛 Troubleshooting

**Container won't start:**
```bash
docker compose logs web
docker compose down -v
docker compose --env-file .env.docker build --no-cache
```

**Static files not loading:**
```bash
docker compose exec web python manage.py collectstatic --noinput --clear
```

**Database connection error:**
```bash
# Pastikan DATABASE_URL ada di .env.docker
grep DATABASE_URL .env.docker

docker compose down
docker compose --env-file .env.docker up -d
```

**View detailed logs:**
```bash
./docker/debug-passenger.sh  # Choose option 5-9
```

## 📖 Full Documentation

Lihat [docs/deployment-domainesia-passenger.md](../docs/deployment-domainesia-passenger.md) untuk panduan lengkap deployment Docker dan Domainesia cPanel.
