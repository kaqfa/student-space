# Docker + Passenger Deployment Guide

Panduan ini adalah referensi utama untuk deployment Student Space dengan stack
Apache + Passenger. Ada dua target yang memakai pola sama:

1. Simulasi lokal dengan Docker
2. Deploy ke Domainesia cPanel (Setup Python App)

## File yang Dipakai

- `Dockerfile`
- `docker-compose.yml`
- `passenger_wsgi.py`
- `public/.htaccess.domainesia.example`
- `.env.docker.example`
- `.env.passenger.example`
- `scripts/deploy_domainesia.sh`
- `deploy/apache/student-space.conf`
- `deploy/scripts/docker-entrypoint.sh`

## 1) Simulasi Lokal dengan Docker

### Prasyarat

- Docker dan Docker Compose tersedia
- Port `8080` dan `8081` tidak dipakai proses lain

### Setup dan Jalankan

```bash
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build
```

### Akses

- Web: `http://localhost:8080`
- Admin: `http://localhost:8080/admin`
- pgAdmin: `http://localhost:8081`

### Yang Terjadi Saat Startup

Container web akan menjalankan:

1. Cek koneksi PostgreSQL
2. `python manage.py migrate --noinput`
3. `python manage.py collectstatic --noinput`
4. Menjalankan Apache + Passenger

### Verifikasi Cepat

```bash
docker compose ps
docker compose exec web passenger-status
curl -I http://localhost:8080
```

## 2) Deploy ke Domainesia cPanel (Passenger)

### Step A - Buat Python App di cPanel

Di menu Setup Python App:

- Python version: `3.11` atau `3.12` (ikuti yang tersedia di akun)
- App directory: `student-space` (atau nama direktori pilihan)
- Application startup file: kosongkan
- Application entry point: kosongkan

### Step B - Upload Source Code

Contoh struktur:

```text
/home/<cpanel-user>/
├── student-space/
│   ├── manage.py
│   ├── passenger_wsgi.py
│   ├── config/
│   ├── apps/
│   └── ...
└── public_html/
```

### Step C - Install Dependencies

Aktifkan virtualenv dari cPanel, lalu:

```bash
cd /home/<cpanel-user>/student-space
pip install --upgrade pip
pip install -r requirements/production.txt
```

### Step D - Buat File .env

```bash
cp .env.passenger.example .env
```

Isi minimal yang wajib:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL`
- `STATIC_ROOT`
- `MEDIA_ROOT`

Contoh:

```dotenv
SECRET_KEY=replace-with-strong-secret
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
STATIC_ROOT=/home/<cpanel-user>/student-space/staticfiles
MEDIA_ROOT=/home/<cpanel-user>/student-space/media
```

### Step E - Migrate dan Collectstatic

```bash
cd /home/<cpanel-user>/student-space
python manage.py migrate --noinput --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
```

### Step F - Konfigurasi .htaccess

Salin template:

```bash
cp public/.htaccess.domainesia.example /home/<cpanel-user>/public_html/.htaccess
```

Kemudian sesuaikan path pada file `.htaccess`.

### Step G - Restart Passenger

```bash
mkdir -p /home/<cpanel-user>/student-space/tmp
touch /home/<cpanel-user>/student-space/tmp/restart.txt
```

Atau klik tombol Restart pada halaman Setup Python App.

## 3) Script Deploy Manual

Script utama deploy adalah:

```bash
bash scripts/deploy_domainesia.sh
```

Script ini cocok dijalankan di server setelah update source code, dan akan:

- install Node dependencies
- build Tailwind CSS
- copy `flowbite.min.js.map` bila tersedia
- setup/aktifkan virtualenv lokal `venv`
- install Python dependencies production
- jalankan migration
- jalankan collectstatic

## 4) Path Mapping: Docker vs Domainesia

| Komponen | Docker (lokal) | Domainesia (contoh) |
|---|---|---|
| Project root | `/var/www/student-space` | `/home/<cpanel-user>/student-space` |
| Venv python | `/var/www/venv/bin/python3` | `/home/<cpanel-user>/virtualenv/<app>/3.12/bin/python` |
| Static root | `/var/www/student-space/staticfiles` | `/home/<cpanel-user>/student-space/staticfiles` |
| Media root | `/var/www/student-space/media` | `/home/<cpanel-user>/student-space/media` |

## 5) Troubleshooting

### A. "No such application" (Passenger)

Cek berurutan:

1. Pastikan `passenger_wsgi.py` ada di project root
2. Pastikan `.htaccess` ada di document root domain
3. Pastikan path `PassengerAppRoot` dan `PassengerPython` benar
4. Pastikan dependency production sudah ter-install di virtualenv
5. Restart Passenger setelah perubahan config

Perintah cepat:

```bash
ls -la /home/<cpanel-user>/student-space/passenger_wsgi.py
ls -la /home/<cpanel-user>/public_html/.htaccess
touch /home/<cpanel-user>/student-space/tmp/restart.txt
```

### B. `ModuleNotFoundError: No module named 'debug_toolbar'`

Biasanya command dijalankan dengan settings development.

Gunakan settings production:

```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Atau pakai flag `--settings=config.settings.production` di setiap command.

### C. Static file tidak muncul

Pastikan:

- `STATIC_ROOT` sudah benar di `.env`
- `collectstatic` sukses
- permission direktori static bisa dibaca web server

Perintah:

```bash
python manage.py collectstatic --noinput --settings=config.settings.production
```

### D. Error database connection

Validasi:

- format `DATABASE_URL`
- host, port, user, password
- privilege user database

### E. WhiteNoise `flowbite.min.js.map` missing

Jika muncul error source map:

```bash
cp node_modules/flowbite/dist/flowbite.min.js.map static/js/
python manage.py collectstatic --noinput --settings=config.settings.production
```

## 6) Pre-Deploy Checklist

- `DEBUG=False`
- `SECRET_KEY` production sudah diganti
- `ALLOWED_HOSTS` dan `CSRF_TRUSTED_ORIGINS` sesuai domain final
- `migrate` sukses
- `collectstatic` sukses
- app di-restart setelah perubahan `.env`/config

## 7) Referensi Ringkas

- Docker quick reference: `docker/README.md`
- Deploy script: `scripts/deploy_domainesia.sh`
- App entrypoint: `passenger_wsgi.py`
