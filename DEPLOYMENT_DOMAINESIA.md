# Panduan Deploy ke Domainesia CloudHost

Panduan lengkap untuk deploy aplikasi Bank Soal ke Domainesia CloudHost dengan PostgreSQL 12.22.

## Prerequisites

- Akun Domainesia CloudHost dengan PostgreSQL 12.22
- Akses SSH ke hosting (jika tersedia)
- Database PostgreSQL sudah dibuat dari cPanel

## Kompatibilitas

✅ **Aplikasi ini SUDAH KOMPATIBEL dengan PostgreSQL 12.22**

- Django 5.0.x mendukung PostgreSQL 12+
- psycopg2-binary 2.9.9+ mendukung PostgreSQL 12+
- Tidak ada fitur PostgreSQL 13+ yang digunakan

⚠️ **Penting**: Jangan upgrade ke Django 5.1+ karena tidak support PostgreSQL 12.

## Langkah-langkah Deployment

### 1. Persiapan Database di cPanel Domainesia

1. Login ke cPanel Domainesia
2. Buka **PostgreSQL Databases**
3. Catat informasi berikut:
   - Database Name (misal: `u123456_banksoal`)
   - Database User (misal: `u123456_banksoal`)
   - Database Password (yang Anda buat)
   - Database Host (biasanya `localhost` atau IP khusus)
   - Database Port (default: `5432`)

### 2. Konfigurasi Environment Variables

Copy file `.env.production.example` menjadi `.env`:

```bash
cp .env.production.example .env
```

Edit file `.env` dan sesuaikan dengan credentials Domainesia Anda:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=generate-secret-key-baru-yang-panjang-dan-acak
DEBUG=False

# Allowed Hosts
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database - PENTING!
DATABASE_ENGINE=postgresql

# Ganti dengan credentials dari cPanel PostgreSQL Anda
DATABASE_URL=postgresql://u123456_banksoal:password123@localhost:5432/u123456_banksoal

# Static & Media Files - sesuaikan dengan path di hosting
STATIC_ROOT=/home/username/public_html/staticfiles
MEDIA_ROOT=/home/username/public_html/media

# Security
SECURE_SSL_REDIRECT=True

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 3. Generate SECRET_KEY

Buat SECRET_KEY baru yang aman:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy hasilnya ke `.env` file.

### 4. Upload Files ke Hosting

Via SSH (jika tersedia):
```bash
# Upload via git clone atau rsync
git clone your-repo-url /home/username/banksoal
cd /home/username/banksoal
```

Via cPanel File Manager:
- Upload semua file proyek ke direktori hosting
- Extract jika dalam bentuk zip

### 5. Install Dependencies

```bash
# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/production.txt
```

### 6. Setup Database

```bash
# Jalankan migrations
python manage.py migrate

# Buat superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 7. Test Koneksi Database

Pastikan koneksi PostgreSQL berhasil:

```bash
python manage.py dbshell
```

Jika berhasil, Anda akan masuk ke PostgreSQL shell. Ketik `\q` untuk keluar.

### 8. Konfigurasi WSGI/Passenger

Domainesia biasanya menggunakan Passenger. Buat file `passenger_wsgi.py` di root proyek:

```python
import sys
import os

# Path ke virtual environment
INTERP = "/home/username/banksoal/venv/bin/python"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Path ke project
sys.path.insert(0, '/home/username/banksoal')

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/home/username/banksoal/.env')

# WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 9. Konfigurasi .htaccess

Buat file `.htaccess` di `public_html`:

```apache
PassengerEnabled On
PassengerAppRoot /home/username/banksoal
PassengerPython /home/username/banksoal/venv/bin/python
PassengerStartupFile passenger_wsgi.py

# Static files
Alias /static /home/username/public_html/staticfiles
Alias /media /home/username/public_html/media

<Directory /home/username/public_html/staticfiles>
    Require all granted
</Directory>

<Directory /home/username/public_html/media>
    Require all granted
</Directory>
```

## Troubleshooting

### Database Connection Error

Jika mendapat error koneksi database:

1. Cek DATABASE_URL format: `postgresql://user:password@host:port/dbname`
2. Pastikan DATABASE_ENGINE=postgresql di .env
3. Cek credentials di cPanel PostgreSQL Databases
4. Pastikan user PostgreSQL punya permission ke database

### Import Error: No module named 'psycopg2'

Install psycopg2:
```bash
pip install psycopg2-binary
```

### Static Files Not Loading

```bash
# Collect static files lagi
python manage.py collectstatic --noinput

# Cek permission
chmod -R 755 /home/username/public_html/staticfiles
```

### 500 Internal Server Error

Check error log di cPanel atau:
```bash
tail -f /home/username/logs/error_log
```

## Maintenance

### Update Aplikasi

```bash
cd /home/username/banksoal
source venv/bin/activate
git pull origin main
pip install -r requirements/production.txt
python manage.py migrate
python manage.py collectstatic --noinput
touch tmp/restart.txt  # Restart Passenger
```

### Backup Database

```bash
# Via command line
pg_dump -U u123456_banksoal -h localhost u123456_banksoal > backup_$(date +%Y%m%d).sql

# Via cPanel - PostgreSQL Databases > Download Backup
```

## Catatan Penting

1. **Jangan upgrade Django ke 5.1+** selama menggunakan PostgreSQL 12
2. **Selalu backup database** sebelum migration
3. **Gunakan HTTPS** untuk production (SSL dari Domainesia)
4. **Set DEBUG=False** di production
5. **Gunakan SECRET_KEY yang unik** per environment

## Support

Jika ada masalah deployment:
- Hubungi support Domainesia: https://www.domainesia.com/ticket/
- Check dokumentasi Django: https://docs.djangoproject.com/
- Issue tracker proyek ini
