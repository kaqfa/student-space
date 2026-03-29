# Docker + Passenger Deployment Guide

Panduan ini menyiapkan dua target deployment untuk proyek Jurnalinvest:

1. Simulasi lokal dengan `Docker + Apache + Passenger`
2. Deploy ke Domainesia `cPanel Setup Python App` berbasis Passenger

Panduan ini mengikuti alur tutorial Domainesia, tetapi disesuaikan untuk repo Django yang **sudah ada**. Jadi kita **tidak** menjalankan `django-admin startproject`.

## Struktur Operasional

File yang dipakai untuk deployment:

- `Dockerfile`
- `docker-compose.yml`
- `passenger_wsgi.py`
- `public/.htaccess.domainesia.example`
- `.env.docker.example`
- `.env.passenger.example`
- `scripts/deploy_domainesia.sh`
- `deploy/apache/jurnalinvest.conf`
- `deploy/scripts/docker-entrypoint.sh`

## 1. Simulasi Lokal dengan Docker

### Prasyarat

- Docker dan Docker Compose tersedia
- PostgreSQL sudah berjalan di host atau stack Docker lain
- Database bisa diakses dari container lewat `host.docker.internal`

### Siapkan Environment

Copy contoh env lalu sesuaikan bila perlu:

```bash
cp .env.docker.example .env.docker
```

Minimal yang perlu dicek:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

### Jalankan Container

```bash
docker compose --env-file .env.docker up --build
```

Startup container akan menjalankan urutan berikut:

1. Cek koneksi database PostgreSQL
2. `python manage.py migrate --noinput`
3. `python manage.py collectstatic --noinput`
4. Start Apache + Passenger

### Akses Aplikasi

Default local URL:

- [http://localhost:8080](http://localhost:8080)

Kalau ingin port lain:

```bash
APP_PORT=8090 docker compose --env-file .env.docker up --build
```

## 2. Mapping ke Tutorial Domainesia cPanel

Tutorial acuan:

- [Deploy website berbasis Python di cPanel Hosting](https://www.domainesia.com/panduan/deploy-website-berbasis-python-di-cpanel-hosting/)

Penyesuaian penting untuk repo ini:

- Jangan buat project Django baru
- Upload source code proyek ini ke direktori app Domainesia
- Gunakan `passenger_wsgi.py` dari repo ini, bukan file kosong/default
- Gunakan template `.htaccess` bila environment cPanel mengikuti pola tutorial
- Gunakan `config.settings` dan `config.wsgi.application`

## 3. Deploy ke Domainesia cPanel

### Step A. Buat aplikasi Python di cPanel

Di `Setup Python App`:

- Python version: `3.11`
- App directory: misalnya `jurnalinvest`
- App domain/URI: sesuaikan domain atau subdomain target
- Application startup file: kosongkan
- Application entry point: kosongkan

### Step B. Upload source code

Upload seluruh isi repo ke direktori aplikasi, misalnya:

```text
/home/<cpanel-user>/jurnalinvest
```

Struktur penting setelah upload:

```text
jurnalinvest/
├── manage.py
├── passenger_wsgi.py
├── public/
│   └── .htaccess.domainesia.example
├── config/
├── apps/
├── templates/
├── static/
└── requirements.txt
```

### Step C. Aktifkan virtualenv dari cPanel

Pakai command virtualenv yang diberikan Domainesia di halaman `Setup Python App`, lalu jalankan:

```bash
cd /home/<cpanel-user>/jurnalinvest
pip install --upgrade pip
pip install -r requirements.txt
```

### Step D. Buat file `.env`

Mulai dari preset Passenger:

```bash
cp .env.passenger.example .env
```

Lalu isi nilai production:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `STATIC_ROOT`
- `MEDIA_ROOT`

Contoh path hosting:

```dotenv
STATIC_ROOT=/home/<cpanel-user>/jurnalinvest/staticfiles
MEDIA_ROOT=/home/<cpanel-user>/jurnalinvest/media
```

### Step E. Jalankan migrasi dan collectstatic

```bash
cd /home/<cpanel-user>/jurnalinvest
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

### Step F. Restart aplikasi Passenger

Gunakan salah satu:

```bash
mkdir -p tmp
touch tmp/restart.txt
```

Atau klik `Restart` pada halaman `Setup Python App`.

## 3A. Script Deploy Manual dari Laptop

Untuk update berikutnya, repo ini menyediakan script deploy manual:

```bash
bash scripts/deploy_domainesia.sh
```

Default script ini:

- sync source code ke `domainesia-app:/home/fahrifir/jurnal-invest`
- activate virtualenv `/home/fahrifir/virtualenv/jurnal-invest/3.11`
- jalankan `pip install -r requirements.txt`
- jalankan `python manage.py check`
- jalankan `python manage.py migrate --noinput`
- jalankan `python manage.py collectstatic --noinput`
- trigger restart Passenger lewat `tmp/restart.txt`

Variable yang bisa dioverride saat perlu:

```bash
SSH_TARGET=domainesia-app \
REMOTE_APP_DIR=/home/fahrifir/jurnal-invest \
REMOTE_VENV_DIR=/home/fahrifir/virtualenv/jurnal-invest/3.11 \
INSTALL_DEPS=0 \
RUN_MIGRATIONS=1 \
RUN_COLLECTSTATIC=1 \
RESTART_PASSENGER=1 \
bash scripts/deploy_domainesia.sh
```

Catatan:

- script tidak menyentuh file `.env`, jadi aman untuk kredensial production yang kamu isi manual di server
- script memakai `rsync`, bukan `git pull`, karena server saat ini belum disiapkan akses clone dari repo private GitHub
- kalau nanti server sudah punya deploy key GitHub, workflow ini bisa diubah ke `git pull`

## 4. Passenger Entrypoint

File `passenger_wsgi.py` di repo ini sudah menjadi entrypoint resmi untuk:

- Apache + Passenger di Docker lokal
- Passenger app di Domainesia cPanel

File ini:

- menambahkan root project ke `sys.path`
- set `DJANGO_SETTINGS_MODULE=config.settings`
- meng-import `config.wsgi.application`

## 5. Template `.htaccess` untuk Domainesia

Repo ini menyediakan template `.htaccess` di:

- `public/.htaccess.domainesia.example`

Template ini mengikuti bentuk konfigurasi tutorial Domainesia:

- `PassengerAppRoot "/home/.../jurnalinvest"`
- `PassengerBaseURI "/"`
- `PassengerPython "/home/.../virtualenv/.../bin/python3.11"`

Untuk simulasi lokal Docker, konfigurasi app tetap di-handle oleh Apache vhost di `deploy/apache/jurnalinvest.conf` karena image Passenger Debian yang dipakai menolak `PassengerAppRoot` di `.htaccess` dengan error `PassengerAppRoot not allowed here`.

Jadi pembagiannya:

- lokal Docker: aktif via Apache vhost
- target Domainesia cPanel: pakai template `.htaccess` ini sebagai acuan

## 6. Pre-Deploy Checklist

Pastikan sebelum go-live:

- `DEBUG=False`
- `SECRET_KEY` production sudah diganti
- `ALLOWED_HOSTS` berisi domain final
- `CSRF_TRUSTED_ORIGINS` berisi URL HTTPS final
- database PostgreSQL bisa diakses dari hosting
- `python manage.py migrate --noinput` sukses
- `python manage.py collectstatic --noinput` sukses
- direktori `STATIC_ROOT` dan `MEDIA_ROOT` writable
- aplikasi sudah di-restart setelah perubahan env

## 7. Troubleshooting

### HTTP 400 Bad Request

Biasanya `ALLOWED_HOSTS` belum benar. Tambahkan domain final dan subdomain yang dipakai.

### Form POST gagal karena CSRF

Periksa `CSRF_TRUSTED_ORIGINS`. Untuk HTTPS, formatnya harus penuh, misalnya:

```dotenv
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

### Static file tidak muncul

Pastikan:

- `STATIC_ROOT` mengarah ke direktori hasil collectstatic
- `python manage.py collectstatic --noinput` sudah dijalankan
- aplikasi di-restart setelah deploy

### Koneksi database gagal

Periksa host, port, username, password, dan whitelist IP pada server PostgreSQL eksternal.

### Passenger tidak memuat app

Pastikan file berikut ada di root proyek:

- `manage.py`
- `passenger_wsgi.py`
- folder `config/`

Lalu restart app dari cPanel atau dengan:

```bash
touch tmp/restart.txt
```
