# Bank Soal SD - Deployment Guide

## 📋 Pre-Deployment Checklist

### 1. **Requirements**
```bash
# Install production requirements
pip install -r requirements/production.txt
```

### 2. **Environment Variables**
Copy `.env.production.example` to `.env` on your production server:

```bash
cp .env.production.example .env
```

Then update the following:
- [ ] `SECRET_KEY` - Generate new one: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] `ALLOWED_HOSTS` - Your domain names
- [ ] `CSRF_TRUSTED_ORIGINS` - HTTPS URLs of your domains
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] Email configuration (if using email features)

### 3. **Database Setup (PostgreSQL)**

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql
```

#### Create Database
```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE banksoal_db;
CREATE USER banksoal_user WITH PASSWORD 'your-strong-password';
ALTER ROLE banksoal_user SET client_encoding TO 'utf8';
ALTER ROLE banksoal_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE banksoal_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE banksoal_db TO banksoal_user;
\q
```

#### Update .env
```
DATABASE_URL=postgresql://banksoal_user:your-strong-password@localhost:5432/banksoal_db
```

### 4. **Static Files**

#### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

This will:
- Collect all static files to `STATIC_ROOT`
- WhiteNoise will serve them efficiently
- Compress and version files for production

### 5. **Database Migrations**
```bash
python manage.py migrate
```

### 6. **Create Superuser**
```bash
python manage.py createsuperuser
```

---

## 🚀 Deployment Options

### Option 1: Traditional Server (VPS)

#### Using Gunicorn + Nginx

**1. Install Gunicorn** (already in requirements/production.txt)

**2. Create Gunicorn systemd service**

`/etc/systemd/system/banksoal.service`:
```ini
[Unit]
Description=Bank Soal SD Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/banksoal
Environment="PATH=/var/www/banksoal/venv/bin"
ExecStart=/var/www/banksoal/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/banksoal.sock \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**3. Start and enable service**
```bash
sudo systemctl start banksoal
sudo systemctl enable banksoal
```

**4. Configure Nginx**

`/etc/nginx/sites-available/banksoal`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/banksoal/staticfiles/;
    }

    location /media/ {
        alias /var/www/banksoal/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/banksoal.sock;
    }
}
```

**5. Enable site and restart Nginx**
```bash
sudo ln -s /etc/nginx/sites-available/banksoal /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

**6. Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

### Option 2: Docker Deployment

**Create Dockerfile**:
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: banksoal_db
      POSTGRES_USER: banksoal_user
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env
    depends_on:
      - db

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

---

### Option 3: Platform as a Service (PaaS)

#### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init

# Add PostgreSQL
railway add postgresql

# Deploy
railway up
```

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn config.wsgi" > Procfile

# Deploy
heroku create banksoal-sd
heroku addons:create heroku-postgresql:mini
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### Render.com
1. Connect GitHub repo
2. Set build command: `pip install -r requirements/production.txt && python manage.py collectstatic --noinput`
3. Set start command: `gunicorn config.wsgi:application`
4. Add PostgreSQL database
5. Set environment variables

---

## 🔒 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (not in git)
- [ ] `ALLOWED_HOSTS` configured
- [ ] `CSRF_TRUSTED_ORIGINS` configured
- [ ] SSL/HTTPS enabled
- [ ] Database password is strong
- [ ] Static files served via WhiteNoise
- [ ] Security headers enabled
- [ ] HSTS enabled
- [ ] Regular backups configured

---

## 📊 Monitoring & Maintenance

### Database Backups
```bash
# Backup
pg_dump -U banksoal_user banksoal_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U banksoal_user banksoal_db < backup_20240117.sql
```

### Logs
```bash
# View application logs
tail -f logs/django.log

# Systemd service logs
sudo journalctl -u banksoal -f
```

### Updates
```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements/production.txt

# Migrate database
python manage.py migrate

# Collect static
python manage.py collectstatic --noinput

# Restart service
sudo systemctl restart banksoal
```

---

## 🧪 Testing Production Setup

```bash
# Run with production settings locally
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py check --deploy

# Test static files
python manage.py collectstatic --noinput --dry-run
```

---

## 📞 Troubleshooting

### Static files not loading
```bash
# Check STATIC_ROOT
python manage.py findstatic admin/css/base.css

# Verify WhiteNoise is in middleware
python manage.py diffsettings | grep MIDDLEWARE
```

### Database connection errors
```bash
# Test PostgreSQL connection
psql -U banksoal_user -d banksoal_db -h localhost

# Check DATABASE_URL format
echo $DATABASE_URL
```

### Permission errors
```bash
# Fix file permissions
sudo chown -R www-data:www-data /var/www/banksoal
sudo chmod -R 755 /var/www/banksoal
```

---

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [WhiteNoise Documentation](http://whitenoise.evans.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
