# Quick Fix: "No such application" Error

## 🎯 Masalah Anda
Error: `No such application (or application not configured) "exp.fahrifirdaus.my.id"`

## 📍 Struktur Direktori Anda
```
/home/fahrifir/
├── student-space/              ← Django source code (dari GitHub)
│   ├── manage.py
│   ├── config/
│   ├── apps/
│   └── .env                    ← Config file
├── exp.fahrifirdaus.my.id/     ← Document root (setup cPanel)
│   ├── passenger_wsgi.py       ⚠️ FILE INI DI SINI (bukan di student-space!)
│   ├── .htaccess               ⚠️ FILE INI DI SINI
│   ├── staticfiles/
│   └── media/
└── virtualenv/
    └── exp.fahrifirdaus.my.id/
        └── 3.12/bin/python     ← Virtual environment (dibuat cPanel)
```

**PENTING:** 
- Source code Django di `/home/fahrifir/student-space/` (dari git clone)
- `passenger_wsgi.py` dan `.htaccess` di `/home/fahrifir/exp.fahrifirdaus.my.id/` (document root)

## ✅ Solusi Cepat

### Opsi 1: Gunakan Script Otomatis (RECOMMENDED)

```bash
# 1. Upload file-file ini ke server:
#    - passenger_wsgi.py
#    - .htaccess  
#    - setup_passenger.sh

# 2. Di server, jalankan:
cd /home/fahrifir/student-space
chmod +x setup_passenger.sh
./setup_passenger.sh
```

Script akan otomatis:
- Copy passenger_wsgi.py ke /home/fahrifir/student-space/
- Copy .htaccess ke /home/fahrifir/exp.fahrifirdaus.my.id/
- Setup static files directories
- Update .env dengan path yang benar
- Collect static files
- Restart Passenger

### Opsi 2: Manual Setup

**1. Buat file passenger_wsgi.py** di `/home/fahrifir/exp.fahrifirdaus.my.id/` (DOCUMENT ROOT!)

```bash
cd /home/fahrifir/exp.fahrifirdaus.my.id
nano passenger_wsgi.py
```

Paste ini:
```python
import sys
import os

# Document root (di mana file ini berada)
DOCUMENT_ROOT = '/home/fahrifir/exp.fahrifirdaus.my.id'

# Source code Django (dari GitHub)
PROJECT_ROOT = '/home/fahrifir/student-space'

# Virtual environment
VENV_PATH = '/home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/python'

if sys.executable != VENV_PATH:
    os.execl(VENV_PATH, VENV_PATH, *sys.argv)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except Exception as e:
    import traceback
    with open(os.path.join(DOCUMENT_ROOT, 'passenger_error.log'), 'w') as f:
        f.write(traceback.format_exc())
    raise
```

Save: Ctrl+O, Enter, Ctrl+X

**2. Buat/Update file .htaccess** di `/home/fahrifir/exp.fahrifirdaus.my.id/`

```bash
cd /home/fahrifir/exp.fahrifirdaus.my.id
nano .htaccess
```

Paste ini:
```apache
PassengerEnabled On
PassengerAppRoot /home/fahrifir/exp.fahrifirdaus.my.id
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

Save: Ctrl+O, Enter, Ctrl+X

**3. Update .env file**

```bash
cd /home/fahrifir/student-space
nano .env
```

Tambahkan/update:
```bash
STATIC_ROOT=/home/fahrifir/exp.fahrifirdaus.my.id/staticfiles
MEDIA_ROOT=/home/fahrifir/exp.fahrifirdaus.my.id/media
```

**4. Collect static files**

```bash
cd /home/fahrifir/student-space
source /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production
```

**5. Set permissions**

```bash
chmod 644 /home/fahrifir/student-space/passenger_wsgi.py
chmod 644 /home/fahrifir/exp.fahrifirdaus.my.id/.htaccess
chmod 755 /home/fahrifir/student-space
```

**6. Restart Passenger**

```bash
mkdir -p /home/fahrifir/student-space/tmp
touch /home/fahrifir/student-space/tmp/restart.txt
```

**7. Test website**

Visit: https://exp.fahrifirdaus.my.id

## 🐛 Jika Masih Error

**Cek error log:**
```bash
# Passenger error log
cat /home/fahrifir/student-space/passenger_error.log

# Server error log
tail -50 ~/logs/error_log
```

**Jalankan debug script:**
```bash
cd /home/fahrifir/student-space
./debug_passenger.sh
```

**Common fixes:**

1. **Virtual env path salah?**
   ```bash
   # Cari path yang benar
   find /home/fahrifir/virtualenv -name "python*"
   # Update di passenger_wsgi.py dan .htaccess
   ```

2. **Django belum install?**
   ```bash
   source /home/fahrifir/virtualenv/exp.fahrifirdaus.my.id/3.12/bin/activate
   pip install -r requirements/production.txt
   ```

3. **File tidak bisa diakses?**
   ```bash
   # Reset permissions
   chmod -R 755 /home/fahrifir/student-space
   chmod 644 /home/fahrifir/student-space/passenger_wsgi.py
   chmod 644 /home/fahrifir/exp.fahrifirdaus.my.id/.htaccess
   ```

## 📞 Support

Jika masih error, kirim informasi ini:
1. Output dari: `./debug_passenger.sh`
2. Isi file: `/home/fahrifir/student-space/passenger_error.log`
3. Last 50 lines dari: `~/logs/error_log`
