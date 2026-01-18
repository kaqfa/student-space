# Deploy Files

File-file deployment untuk aplikasi Bank Soal SD.

## 📁 Files

### 1. `DEPLOYMENT_DOMAINESIA.md`
Panduan lengkap deployment ke Domainesia CloudHost.

**Isi:**
- Prerequisites (Node.js, PostgreSQL, Python)
- Setup Node.js di server
- Langkah deployment (automated & manual)
- Troubleshooting common issues
- Maintenance guide

### 2. `deploy_domainesia.sh`
Script otomatis untuk deployment.

**Yang dilakukan script:**
1. Install Node.js dependencies (`npm install`)
2. Build Tailwind CSS (`npm run build`)
3. Copy flowbite source map
4. Setup Python virtual environment
5. Install Python dependencies
6. Run database migrations
7. Collect static files

**Cara pakai:**
```bash
chmod +x deploy_domainesia.sh
./deploy_domainesia.sh
```

### 3. `.env.production.example`
Template konfigurasi production environment.

**Cara pakai:**
```bash
cp .env.production.example .env
nano .env  # Edit dengan credentials Anda
```

## 🚀 Quick Deploy

```bash
# 1. Setup .env
cp .env.production.example .env
# Edit .env dengan credentials Domainesia

# 2. Deploy
./deploy_domainesia.sh

# 3. Create superuser
source venv/bin/activate
python manage.py createsuperuser --settings=config.settings.production

# 4. Restart server
touch tmp/restart.txt
```

## 🐛 Common Issues

### Error: `tailwindcss: command not found`
**Solusi:**
```bash
npm install
npm run build
```

### Error: `The file 'js/flowbite.min.js.map' could not be found`
**Solusi:**
```bash
cp node_modules/flowbite/dist/flowbite.min.js.map static/js/
python manage.py collectstatic --noinput --settings=config.settings.production
```

### Error: `No module named 'debug_toolbar'`
**Solusi:**
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
# Atau gunakan flag --settings di setiap command
```

## 📚 Dokumentasi Lengkap

Lihat `DEPLOYMENT_DOMAINESIA.md` untuk panduan lengkap.
