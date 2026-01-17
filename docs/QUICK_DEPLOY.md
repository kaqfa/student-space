# Quick Reference: Deployment Commands

## 🚀 Quick Deploy

```bash
# 1. Setup environment
cp .env.production.example .env
# Edit .env with your settings

# 2. Run deployment script
./deploy.sh

# 3. Create superuser
python manage.py createsuperuser

# 4. Start server
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## 📦 Requirements

```bash
# Production
pip install -r requirements/production.txt

# Development
pip install -r requirements/development.txt
```

## 🗄️ Database

```bash
# PostgreSQL setup
sudo -u postgres psql
CREATE DATABASE banksoal_db;
CREATE USER banksoal_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE banksoal_db TO banksoal_user;

# Migrate
python manage.py migrate

# Create admin
python manage.py createsuperuser
```

## 📁 Static Files

```bash
# Collect static files (production)
python manage.py collectstatic --noinput

# Development (Tailwind)
npm run dev          # Watch mode
npm run build        # Build once
```

## 🧪 Testing

```bash
# All tests
pytest

# Specific app
pytest apps/quizzes/tests/

# Coverage
pytest --cov=apps --cov-report=html
```

## 🔄 Update Production

```bash
git pull origin main
pip install -r requirements/production.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart banksoal  # or your service name
```

## 🐳 Docker

```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
