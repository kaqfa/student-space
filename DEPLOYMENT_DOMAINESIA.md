# Panduan Deploy ke Domainesia CloudHost

Panduan lengkap untuk deploy aplikasi Bank Soal ke Domainesia CloudHost dengan PostgreSQL 12.22.

## 🚀 Quick Start

Jika sudah pernah deploy dan hanya perlu quick reference:

```bash
# 1. Setup environment
cp .env.production.example .env
# Edit .env dengan credentials Domainesia

# 2. Run deployment script
chmod +x deploy_domainesia.sh
./deploy_domainesia.sh

# 3. Create superuser
source venv/bin/activate
python manage.py createsuperuser --settings=config.settings.production

# 4. Restart server
touch tmp/restart.txt
```

**⚠️ Common Issues:**
- `tailwindcss: command not found` → Jalankan `npm install`
- `flowbite.min.js.map not found` → Copy file: `cp node_modules/flowbite/dist/flowbite.min.js.map static/js/`
- `No module named debug_toolbar` → Set `DJANGO_SETTINGS_MODULE=config.settings.production`

Untuk panduan lengkap, lanjut baca di bawah 👇

## Prerequisites

- Akun Domainesia CloudHost dengan PostgreSQL 12.22
- Akses SSH ke hosting (jika tersedia)
- Database PostgreSQL sudah dibuat dari cPanel
- **Node.js 16+ dan npm** (untuk build Tailwind CSS)
- Python 3.10+

## Kompatibilitas

✅ **Aplikasi ini SUDAH KOMPATIBEL dengan PostgreSQL 12.22**

- Django 5.0.x mendukung PostgreSQL 12+
- psycopg2-binary 2.9.9+ mendukung PostgreSQL 12+
- Tidak ada fitur PostgreSQL 13+ yang digunakan

⚠️ **Penting**: Jangan upgrade ke Django 5.1+ karena tidak support PostgreSQL 12.

## Setup Node.js di Server (PENTING!)

Aplikasi ini membutuhkan Node.js untuk build CSS dengan Tailwind. **Pastikan Node.js sudah terinstall** sebelum deployment.

### Cek Versi Node.js dan npm

```bash
# Cek apakah Node.js sudah terinstall
node --version  # Harus 16.x atau lebih tinggi
npm --version   # Harus 8.x atau lebih tinggi
```

### Install Node.js di Domainesia (jika belum ada)

Jika Node.js belum terinstall di server Domainesia:

**Via cPanel (Setup Node.js):**
1. Login ke cPanel Domainesia
2. Cari menu **"Setup Node.js App"** atau **"Node.js Selector"**
3. Pilih versi Node.js 16.x atau lebih tinggi
4. Set document root sesuai project Anda

**Via SSH (menggunakan NodeSource):**
```bash
# Install Node.js 18.x LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
sudo apt-get install -y nodejs

# Verifikasi instalasi
node --version
npm --version
```

**Via NVM (Node Version Manager) - Recommended:**
```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc

# Install Node.js LTS
nvm install --lts
nvm use --lts

# Verifikasi
node --version
npm --version
```

### Test Node.js Setup

```bash
# Test npm install
cd /path/to/your/project
npm install

# Jika berhasil, lanjut test build
npm run build

# Harus muncul: "Done in XXXms"
```

## Langkah-langkah Deployment

### Opsi 1: Menggunakan Deployment Script (Recommended)

**Langkah-langkah:**

1. **Upload project ke server**
   ```bash
   # Via git (recommended)
   git clone your-repo-url /home/username/banksoal
   cd /home/username/banksoal
   
   # Atau upload manual via cPanel File Manager
   ```

2. **Konfigurasi .env file**
   ```bash
   # Copy template ke .env
   cp .env.production.example .env
   
   # Edit .env dengan credentials Domainesia Anda
   nano .env  # atau editor lain
   ```
   
   Minimal yang harus diisi:
   - `SECRET_KEY` (generate baru)
   - `ALLOWED_HOSTS` (domain Anda)
   - `DATABASE_URL` (dari cPanel PostgreSQL)
   - `STATIC_ROOT` dan `MEDIA_ROOT` (path di server)

3. **Jalankan deployment script**
   ```bash
   # Beri permission executable
   chmod +x deploy_domainesia.sh
   
   # Jalankan script
   ./deploy_domainesia.sh
   ```

4. **Buat superuser** (setelah script selesai)
   ```bash
   source venv/bin/activate
   python manage.py createsuperuser --settings=config.settings.production
   ```

5. **Restart web server**
   ```bash
   # Untuk Passenger
   mkdir -p tmp
   touch tmp/restart.txt
   ```

**Catatan:** Script ini akan otomatis:
- Install Node.js dependencies (`npm install`)
- Build CSS dengan Tailwind (`npm run build`)
- Copy file flowbite source map (mengatasi WhiteNoise error)
- Setup virtual environment
- Install Python dependencies
- Run migrations
- Collect static files

### Opsi 2: Manual Step-by-Step

Jika ingin menjalankan manual atau untuk troubleshooting:

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
# Install Node.js dependencies (untuk Tailwind CSS)
npm install

# Build CSS files
npm run build

# Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/production.txt
```

### 6. Setup Database

**PENTING**: Pastikan menggunakan production settings!

```bash
# Set environment variable untuk production settings
export DJANGO_SETTINGS_MODULE=config.settings.production

# Atau gunakan flag --settings di setiap command:
# python manage.py migrate --settings=config.settings.production

# Jalankan migrations
python manage.py migrate

# Buat superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

**Alternatif**: Set di .env file (sudah ada di .env.production.example):
```bash
DJANGO_SETTINGS_MODULE=config.settings.production
```

### 7. Test Koneksi Database

Pastikan koneksi PostgreSQL berhasil:

```bash
# Pastikan DJANGO_SETTINGS_MODULE sudah di-set
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

### 10. Setup Passenger - Contoh untuk exp.fahrifirdaus.my.id

**Struktur Direktori Domainesia:**

Domainesia biasanya menggunakan struktur seperti ini:
```
/home/fahrifir/
├── student-space/              ← Aplikasi Django
│   ├── manage.py
│   ├── config/
│   ├── apps/
│   └── passenger_wsgi.py       ← File ini di sini
├── exp.fahrifirdaus.my.id/     ← Document root domain
│   ├── .htaccess               ← File ini di sini
│   ├── staticfiles/
│   └── media/
└── virtualenv/
    └── exp.fahrifirdaus.my.id/
        └── 3.12/               ← Virtual env (dibuat cPanel)
            └── bin/python
```

**File passenger_wsgi.py** (di `/home/fahrifir/student-space/`):
```python
import sys
import os

PROJECT_ROOT = '/home/fahrifir/student-space'
VENV_PATH = '/home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python'

if sys.executable != VENV_PATH:
    os.execl(VENV_PATH, VENV_PATH, *sys.argv)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**File .htaccess** (di `/home/fahrifir/exp.fahrifirdaus.my.id/`):
```apache
PassengerEnabled On
PassengerAppRoot /home/fahrifir/student-space
PassengerPython /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python
PassengerStartupFile passenger_wsgi.py
PassengerAppEnv production

Alias /static /home/fahrifir/exp.fahrifirdaus.my.id/staticfiles
Alias /media /home/fahrifir/exp.fahrifirdaus.my.id/media

<Directory /home/fahrifir/exp.fahrifirdaus.my.id/staticfiles>
    Options -Indexes +FollowSymLinks
    Require all granted
</Directory>

<Directory /home/fahrifir/exp.fahrifirdaus.my.id/media>
    Options -Indexes +FollowSymLinks
    Require all granted
</Directory>
```

**Setup .env file**:
```bash
STATIC_ROOT=/home/fahrifir/exp.fahrifirdaus.my.id/staticfiles
MEDIA_ROOT=/home/fahrifir/exp.fahrifirdaus.my.id/media
```

**Automated Setup Script:**

Gunakan script untuk setup otomatis:
```bash
# Di local machine, jalankan:
chmod +x setup_passenger.sh

# Upload setup_passenger.sh, passenger_wsgi.py, dan .htaccess ke server
# Kemudian di server:
cd /home/fahrifir/student-space
./setup_passenger.sh
```

## Troubleshooting

### Error: "No such application" (Passenger)

Error ini adalah masalah paling umum di Passenger. Penyebabnya:

**1. File passenger_wsgi.py tidak ada atau di lokasi salah**

```bash
# Cek apakah file ada
ls -la /home/fahrifir/student-space/passenger_wsgi.py

# Jika tidak ada, buat file ini
nano /home/fahrifir/student-space/passenger_wsgi.py
# Copy isi dari section 10 di atas
```

**2. Path di .htaccess salah**

```bash
# Edit .htaccess
nano /home/fahrifir/exp.fahrifirdaus.my.id/.htaccess

# Pastikan:
# PassengerAppRoot = path ke folder dengan passenger_wsgi.py
# PassengerPython = path ke venv/bin/python yang benar
```

**3. Virtual environment belum diaktifkan atau path salah**

```bash
# Cek apakah venv ada
ls -la /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python

# Jika tidak ada, cari venv yang benar:
find /home/fahrifir/virtualenv -name "python*"

# Update path di passenger_wsgi.py dengan path yang benar
```

**4. Permission file salah**

```bash
# Set permission yang benar
chmod 644 /home/fahrifir/student-space/passenger_wsgi.py
chmod 755 /home/fahrifir/student-space
chmod 644 /home/fahrifir/exp.fahrifirdaus.my.id/.htaccess
```

**5. Django tidak ter-install di virtual environment**

```bash
# Aktivasi venv dan cek Django
source /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/activate
python -c "import django; print(django.get_version())"

# Jika error, install dependencies
pip install -r requirements/production.txt
```

**6. WSGI import error**

```bash
# Test import passenger_wsgi
cd /home/fahrifir/student-space
source /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/activate
python -c "import passenger_wsgi"

# Cek error di log
cat /home/fahrifir/student-space/passenger_error.log
# atau
cat ~/logs/error_log
```

**7. Restart Passenger setelah perubahan**

```bash
# Setiap kali ubah passenger_wsgi.py atau .htaccess, restart:
mkdir -p /home/fahrifir/student-space/tmp
touch /home/fahrifir/student-space/tmp/restart.txt
```

**Debug Script:**

Gunakan script debug untuk cek konfigurasi:
```bash
cd /home/fahrifir/student-space
./debug_passenger.sh
```

Script ini akan cek:
- Apakah passenger_wsgi.py ada
- Apakah virtual environment benar
- Apakah Django ter-install
- Path dan permission file
- Dan memberikan rekomendasi fix

### Database Connection Error

Jika mendapat error koneksi database:

1. Cek DATABASE_URL format: `postgresql://user:password@host:port/dbname`
2. Pastikan DATABASE_ENGINE=postgresql di .env
3. Cek credentials di cPanel PostgreSQL Databases
4. Pastikan user PostgreSQL punya permission ke database

### ModuleNotFoundError: No module named 'debug_toolbar'

Error ini terjadi karena menggunakan development settings di production. **Solusi**:

1. **Set DJANGO_SETTINGS_MODULE dengan benar**:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
```

2. **Atau gunakan flag --settings di setiap command**:
```bash
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
```

3. **Pastikan .env file sudah benar**:
```bash
# File .env harus berisi:
DJANGO_SETTINGS_MODULE=config.settings.production
```

4. **Pastikan install dari production requirements**:
```bash
pip install -r requirements/production.txt
# JANGAN install dari requirements/development.txt di production!
```

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

### WhiteNoise MissingFileError (flowbite.min.js.map)

Jika mendapat error `The file 'js/flowbite.min.js.map' could not be found`:

```bash
# Copy source map file dari node_modules ke static
cp node_modules/flowbite/dist/flowbite.min.js.map static/js/

# Collect static files lagi
python manage.py collectstatic --noinput --settings=config.settings.production
```

### Tailwindcss Command Not Found

Jika `npm run build` error dengan `tailwindcss: command not found`:

```bash
# Install node modules terlebih dahulu
npm install

# Kemudian build CSS
npm run build
```

**Catatan**: Pastikan Node.js dan npm sudah terinstall di server.

## Maintenance

### Update Aplikasi

```bash
cd /home/username/banksoal
source venv/bin/activate

# Pull latest changes
git pull origin main

# Update Node.js dependencies (jika ada perubahan di package.json)
npm install

# Rebuild CSS (jika ada perubahan di Tailwind config atau CSS)
npm run build

# Copy flowbite source map (jika belum ada)
[ ! -f static/js/flowbite.min.js.map ] && cp node_modules/flowbite/dist/flowbite.min.js.map static/js/

# Update Python dependencies
pip install -r requirements/production.txt

# Run migrations
python manage.py migrate --settings=config.settings.production

# Collect static files
python manage.py collectstatic --noinput --settings=config.settings.production

# Restart Passenger
touch tmp/restart.txt
```

### Backup Database

```bash
# Via command line
pg_dump -U u123456_banksoal -h localhost u123456_banksoal > backup_$(date +%Y%m%d).sql

# Via cPanel - PostgreSQL Databases > Download Backup
```

## Catatan Penting

1. **Node.js adalah WAJIB** - Aplikasi ini membutuhkan Node.js untuk build Tailwind CSS
   - Minimal Node.js 16.x
   - Jalankan `npm install` dan `npm run build` setiap kali deploy/update
   
2. **Flowbite Source Map** - File `flowbite.min.js.map` harus ada di `static/js/`
   - Jika hilang, copy dari: `node_modules/flowbite/dist/flowbite.min.js.map`
   - Error WhiteNoise berarti file ini tidak ada

3. **Jangan upgrade Django ke 5.1+** selama menggunakan PostgreSQL 12
   
4. **Selalu backup database** sebelum migration

5. **Gunakan HTTPS** untuk production (SSL dari Domainesia)

6. **Set DEBUG=False** di production

7. **Gunakan SECRET_KEY yang unik** per environment

8. **Build CSS sebelum collectstatic**
   ```bash
   # Urutan yang benar:
   npm install          # 1. Install dependencies
   npm run build        # 2. Build CSS
   collectstatic        # 3. Collect semua static files
   ```

## Support

Jika ada masalah deployment:
- Hubungi support Domainesia: https://www.domainesia.com/ticket/
- Check dokumentasi Django: https://docs.djangoproject.com/
- Issue tracker proyek ini
