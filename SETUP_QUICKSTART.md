# Setup Passenger - Quick Guide

## ✅ Struktur Direktori yang Benar

```
/home/fahrifir/
├── student-space/               ← Source code Django (dari git clone)
│   ├── manage.py
│   ├── config/
│   ├── apps/
│   ├── .env                     ← Config di sini
│   └── setup_passenger.sh       ← Script di sini
│
├── exp.fahrifirdaus.my.id/      ← Document root (cPanel setup)
│   ├── passenger_wsgi.py        ← Di-copy ke sini oleh setup script
│   ├── .htaccess                ← Di-copy ke sini oleh setup script
│   ├── staticfiles/             ← Dibuat oleh collectstatic
│   └── media/
│
└── virtualenv/
    └── exp.fahrifirdaus.my.id/3.12/
        └── bin/python           ← Virtual env (dibuat cPanel)
```

## 🚀 Cara Setup (Setelah Git Pull)

### 1. Di /home/fahrifir/student-space (source code):

```bash
cd /home/fahrifir/student-space

# Pull latest changes
git pull origin main

# Setup .env jika belum ada
if [ ! -f .env ]; then
    cp .env.production.example .env
    nano .env  # Edit dengan credentials Anda
fi

# Jalankan setup script
chmod +x setup_passenger.sh
./setup_passenger.sh
```

### 2. Test Website

Visit: https://exp.fahrifirdaus.my.id

## 📋 Apa yang Dilakukan setup_passenger.sh?

1. **Copy passenger_wsgi.py** dari student-space/ ke exp.fahrifirdaus.my.id/
2. **Copy .htaccess** dari student-space/ ke exp.fahrifirdaus.my.id/
3. **Buat directories** staticfiles/ dan media/ di exp.fahrifirdaus.my.id/
4. **Update .env** dengan STATIC_ROOT dan MEDIA_ROOT yang benar
5. **Collect static files** ke exp.fahrifirdaus.my.id/staticfiles/
6. **Restart Passenger** dengan touch tmp/restart.txt

## 🔑 Key Points

### PassengerAppRoot
```
PassengerAppRoot /home/fahrifir/exp.fahrifirdaus.my.id
```
**BUKAN** `/home/fahrifir/student-space/`!

Passenger mencari `passenger_wsgi.py` di PassengerAppRoot.

### passenger_wsgi.py Location
File ini ada di **document root** (`exp.fahrifirdaus.my.id/`), tapi `sys.path.insert()` menambahkan source code directory (`student-space/`) sehingga Django bisa di-import.

### .env Location
File `.env` tetap di `/home/fahrifir/student-space/.env` karena itu bagian dari source code.

## 🐛 Troubleshooting

### Error: "No such application"

```bash
# Cek apakah file ada
ls -la /home/fahrifir/exp.fahrifirdaus.my.id/passenger_wsgi.py
ls -la /home/fahrifir/exp.fahrifirdaus.my.id/.htaccess

# Jika tidak ada, jalankan setup script lagi
cd /home/fahrifir/student-space
./setup_passenger.sh
```

### Error: "ModuleNotFoundError: No module named 'config'"

Berarti `PROJECT_ROOT` di `passenger_wsgi.py` tidak benar. Cek:

```bash
cat /home/fahrifir/exp.fahrifirdaus.my.id/passenger_wsgi.py | grep PROJECT_ROOT
# Harus: PROJECT_ROOT = '/home/fahrifir/student-space'
```

### Restart Passenger

```bash
mkdir -p /home/fahrifir/exp.fahrifirdaus.my.id/tmp
touch /home/fahrifir/exp.fahrifirdaus.my.id/tmp/restart.txt
```

### Check Error Log

```bash
# Passenger error log
cat /home/fahrifir/exp.fahrifirdaus.my.id/passenger_error.log

# Server error log
tail -50 ~/logs/error_log
```

## 🔄 Update Workflow

Untuk update aplikasi di masa depan:

```bash
cd /home/fahrifir/student-space
git pull origin main
npm install                    # Jika ada perubahan package.json
npm run build                  # Build CSS
./setup_passenger.sh           # Re-setup Passenger (copy files, collectstatic, restart)
```

Atau lebih singkat:

```bash
cd /home/fahrifir/student-space && git pull && ./setup_passenger.sh
```
