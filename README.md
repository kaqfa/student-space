# 📚 Ruang Belajar

<div align="center">

![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-2.x-3366CC?style=for-the-badge)

**Platform homeschooling & persiapan ujian (TKA) untuk jenjang SD–SMP: bank soal terstruktur, try-out simulasi, pelacakan lintas tahun ajaran, dan analitik mendalam.**

</div>

---

## 🌟 Overview

Ruang Belajar (codebase: `student-space`) adalah platform pembelajaran berbasis web untuk membantu orang tua homeschooling mengelola pendidikan anak dari **SD hingga SMP**. Platform menyediakan bank soal terstruktur, kuis & try-out simulasi, pelacakan perkembangan **lintas tahun ajaran**, dan analitik mendalam — sehingga orang tua punya visibilitas penuh atas kekuatan dan kelemahan belajar anak.

Selain homeschooling, platform menargetkan pasar **persiapan Tes Kemampuan Akademik (TKA)** untuk masuk SD/SMP/program unggulan: try-out berbasis blueprint, readiness score, dan rencana belajar otomatis.

> **Arah produk (v2):** dokumen acuan terbaru adalah [docs/prd-v2.md](docs/prd-v2.md). README ini mendeskripsikan visi target v2. **Progress penyelarasan** ada di [docs/implementation-progress.md](docs/implementation-progress.md): fondasi akademik (`academic`: Grade/AcademicYear/Enrollment, jenjang SD+SMP) & unit `Family` sudah ada; modul try-out, subscription, dan riwayat lintas tahun masih dalam pengerjaan. Lihat [docs/ui-improvement-plan.md](docs/ui-improvement-plan.md) untuk rencana migrasi UI.

## ✨ Fitur Utama

### 📝 Manajemen Bank Soal
- **Multi-tipe soal:** Pilihan ganda, Essay, Isian, Benar/Salah
- **Kategori bertingkat:** Jenjang → Kelas → Mata Pelajaran → Topik → Soal
- **Tagging system:** Cross-cutting (numerasi, literasi, HOTS, problem-solving, dll.)
- **Kompetensi Dasar (KD):** Mapping ke kurikulum nasional
- **Bulk import:** Import soal via JSON dengan audit trail & rollback
- **LaTeX support:** Render rumus matematika dengan KaTeX

### 🎯 Quiz & Try-out Engine
- **Practice Mode:** Tanpa timer, feedback langsung setelah jawab
- **Timed Quiz:** Dengan countdown timer & auto-submit
- **Custom Quiz:** Konfigurasi quiz spesifik (filter topik/tag/kesulitan)
- **Try-out berbasis Blueprint:** Cetak biru ujian (TKA SD/SMP) dengan seksi & bobot *(target v2)*
- **Readiness Score & Countdown:** Prediksi kesiapan ujian dari tren try-out *(target v2)*
- **Study Plan otomatis:** Rekomendasi area lemah dari hasil try-out *(target v2)*

### 📊 Progress Tracking & Analytics
- **Per-topic/tag tracking:** Progress di setiap topik & skill
- **Skill heatmap & mastery matrix:** Visualisasi kekuatan & kelemahan
- **KD coverage:** Track cakupan kurikulum
- **Trend analysis:** Grafik perkembangan dari waktu ke waktu
- **Riwayat lintas tahun ajaran:** Timeline perkembangan antar kelas *(target v2)*
- **Laporan PDF:** Generate & share laporan progress/try-out *(target v2)*

### 👥 Multi-Role Access
- **Admin:** Pengelola platform via **Django Admin** (konten, user, konfigurasi)
- **Orang Tua:** Custom UI — kelola anak, pantau progress, kelola langganan
- **Pengajar (opsional):** Django Admin terbatas untuk siswa yang di-assign
- **Siswa:** Custom UI — mengerjakan kuis/try-out & melihat progress sendiri

### 💳 Monetisasi *(target v2)*
- **Freemium:** Tier Free / Basic / Pro dengan feature gating berbasis langganan
- **Payment gateway:** Midtrans / Xendit
- **Subscription per Family** dengan grace period

### 📱 Modern UI/UX
- **Mobile-first:** Dioptimalkan untuk smartphone (mayoritas pengguna)
- **HTMX-powered:** Interaksi dinamis tanpa full page reload
- **Clean interface:** Custom UI hanya untuk Orang Tua & Siswa; admin via Django Admin

---

## 🚀 Quick Start

> **⚙️ Proyek ini berbasis Docker.** Semua perintah aplikasi (manage.py, pytest, migrate, seed) dijalankan **di dalam container**, bukan di host. **Jangan** membuat virtualenv (`venv/`, `.venv`) di repo ini. Pola perintah: `docker compose exec web <perintah>`.

### Prerequisites
- **Docker & Docker Compose**
- Node.js 18+ — hanya untuk build Tailwind CSS (tooling host, opsional)

### Menjalankan (Docker)

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd student-space
   ```

2. **Siapkan environment**
   ```bash
   cp .env.docker.example .env.docker
   # Edit .env.docker jika perlu (SECRET_KEY, DB credentials, dll)
   ```

3. **Jalankan stack**
   ```bash
   docker compose --env-file .env.docker up --build -d
   ```
   Container `web` (Apache+Passenger) + `db` (PostgreSQL) akan berjalan.

4. **Migrasi & seed data awal** (di dalam container)
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py seed_initial_data   # groups+perms & academic reference
   ```

5. **Buat superuser**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. **Build Tailwind CSS** (tooling Node, di host)
   ```bash
   npm install
   npm run build
   ```

7. **Akses aplikasi**
   ```
   Web:     http://localhost:8080
   Admin:   http://localhost:8080/admin
   pgAdmin: http://localhost:8081
   ```

> Source di-mount sebagai volume — edit file di host langsung ter-reflect di container. Untuk perintah lain (shell, dll): `docker compose exec web bash`.

---

## 📁 Project Structure

```
student-space/
├── apps/                    # Django applications
│   ├── accounts/           # User+role(admin/parent/student/tutor), Family, profiles, ParentStudent
│   ├── academic/           # EducationLevel, Grade, AcademicYear, GradeSubject, Enrollment
│   ├── students/           # DEPRECATED (student = User(role=student) + ParentStudent)
│   ├── subjects/           # Subjects & topics
│   ├── questions/          # Question bank
│   ├── quizzes/            # Quiz engine
│   ├── analytics/          # Progress tracking
│   └── core/               # Shared utilities, seed_initial_data
├── config/                 # Django project settings
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
├── deploy/                 # Deployment configurations
│   ├── apache/
│   │   └── student-space.conf   # Apache VirtualHost (Docker)
│   └── scripts/
│       └── docker-entrypoint.sh # Container startup script
├── scripts/                # Helper scripts
│   └── deploy_domainesia.sh     # Manual deploy script ke cPanel
├── public/                 # Document root (digunakan Passenger)
│   └── .htaccess.domainesia.example  # Template .htaccess untuk cPanel
├── templates/              # HTML templates
├── static/                 # Static files (CSS, JS, images)
├── media/                  # User uploaded files
├── docs/                   # Documentation
│   ├── spec.md            # Technical specification
│   ├── prd.md             # Product requirements
│   └── deployment-domainesia-passenger.md  # Panduan deployment Passenger
├── Dockerfile              # Docker image (Apache + Passenger)
├── docker-compose.yml      # Docker stack (web + db + pgadmin)
├── passenger_wsgi.py       # WSGI entrypoint (Docker & Domainesia)
├── .env.docker.example     # Template env untuk Docker lokal
├── .env.passenger.example  # Template env untuk Domainesia
└── requirements/           # Python dependencies
```

---

## 🚢 Deployment

Proyek ini mendukung dua target deployment yang menggunakan stack yang sama: **Apache + Passenger**.

> Dokumentasi lengkap: [docs/deployment-domainesia-passenger.md](docs/deployment-domainesia-passenger.md)

---

### Simulasi Lokal dengan Docker

Stack Docker menjalankan Apache + Passenger di dalam container — identik dengan lingkungan Domainesia cPanel — sehingga dapat dipakai untuk testing sebelum push ke production.

**Prasyarat:** Docker dan Docker Compose tersedia.

```bash
# 1. Siapkan environment
cp .env.docker.example .env.docker
# Edit .env.docker jika perlu (SECRET_KEY, DB credentials, dll)

# 2. Jalankan container
docker compose --env-file .env.docker up --build

# 3. Akses aplikasi
#    Web:    http://localhost:8080
#    Admin:  http://localhost:8080/admin  (admin / admin123)
#    pgAdmin: http://localhost:8081
```

Perintah berguna setelah container berjalan:

```bash
# Cek status Passenger
docker compose exec web passenger-status

# Tail logs Apache + Passenger
docker compose logs -f web

# Masuk ke shell container
docker compose exec web bash

# Restart aplikasi Passenger (tanpa rebuild container)
docker compose exec web passenger-config restart-app /var/www/student-space

# Hentikan semua container
docker compose down
docker compose down -v   # termasuk hapus volumes
```

---

### Deploy ke Domainesia cPanel (Passenger)

Domainesia menggunakan **cPanel → Setup Python App** yang menjalankan Passenger secara otomatis.

> Catatan: virtualenv di bawah ini **khusus environment cPanel Domainesia** (dikelola cPanel). Untuk **dev lokal jangan bikin venv** — pakai Docker (lihat [Quick Start](#-quick-start)).

#### A. Buat aplikasi Python di cPanel

Di menu **Setup Python App**:
- Python version: `3.12`
- App directory: `student-space` (atau nama direktori pilihan)
- App domain/URI: sesuaikan domain atau subdomain target
- Application startup file & entry point: **kosongkan**

#### B. Upload source code

Clone atau upload seluruh isi repo ke direktori aplikasi:

```bash
# Via SSH
cd /home/<cpanel-user>
git clone <repo-url> student-space
```

Struktur direktori penting setelah upload:

```text
student-space/
├── manage.py
├── passenger_wsgi.py      ← entrypoint Passenger
├── public/
│   └── .htaccess.domainesia.example
├── config/
└── requirements/
```

#### C. Install dependencies

Aktifkan virtualenv dari cPanel, lalu:

```bash
cd /home/<cpanel-user>/student-space
pip install --upgrade pip
pip install -r requirements/production.txt
```

#### D. Buat file `.env`

```bash
cp .env.passenger.example .env
# Edit .env: isi SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL, STATIC_ROOT, dll
```

Contoh nilai penting:

```dotenv
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
STATIC_ROOT=/home/<cpanel-user>/student-space/staticfiles
MEDIA_ROOT=/home/<cpanel-user>/student-space/media
```

#### E. Jalankan migrasi dan collectstatic

```bash
cd /home/<cpanel-user>/student-space
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

#### F. Konfigurasi `.htaccess`

Passenger di cPanel dikonfigurasi via `.htaccess` di document root domain. Gunakan template:

```bash
# Salin template ke document root domain
cp public/.htaccess.domainesia.example /home/<cpanel-user>/public_html/.htaccess
# Edit path sesuai environment
```

Isi minimal `.htaccess`:

```apache
PassengerEnabled On
PassengerAppRoot /home/<cpanel-user>/student-space
PassengerPython /home/<cpanel-user>/virtualenv/student-space/3.12/bin/python
PassengerStartupFile passenger_wsgi.py
PassengerAppEnv production
```

#### G. Restart Passenger

```bash
mkdir -p /home/<cpanel-user>/student-space/tmp
touch /home/<cpanel-user>/student-space/tmp/restart.txt
```

Atau klik **Restart** pada halaman Setup Python App di cPanel.

---

### Deploy Update (Script Otomatis)

Untuk update berikutnya dari laptop:

```bash
bash scripts/deploy_domainesia.sh
```

---

### Pre-Deploy Checklist

- `DEBUG=False`
- `SECRET_KEY` production sudah diganti
- `ALLOWED_HOSTS` berisi domain final
- `CSRF_TRUSTED_ORIGINS` berisi URL HTTPS final
- `python manage.py migrate --noinput` sukses
- `python manage.py collectstatic --noinput` sukses
- Direktori `STATIC_ROOT` dan `MEDIA_ROOT` writable
- Aplikasi sudah di-restart setelah perubahan env

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Product Requirements v2](docs/prd-v2.md) | **PRD terbaru (acuan utama)** — homeschooling SD–SMP + TKA prep |
| [v2 Upgrade Plan](docs/v2-upgrade-plan.md) | Rencana upgrade backend/data model + master sequence (UI+backend) |
| [UI Improvement Plan](docs/ui-improvement-plan.md) | Rencana redesign UI ortu/siswa + migrasi admin ke Django Admin |
| [Technical Spec](docs/spec.md) | Detailed technical specification (v1) |
| [Product Requirements v1](docs/prd.md) | PRD lama (SD only) — historis |
| [Implementation Progress](docs/implementation-progress.md) | Status fase B0–B8 / U0–U5 |
| [Deployment Guide](docs/deployment-domainesia-passenger.md) | Panduan deploy Passenger (Docker & cPanel) |
| [AGENTS.md](AGENTS.md) | AI agent working guidelines |
| [Testing Guidelines](.agent/TESTING_GUIDELINES.md) | Testing strategy and best practices |
| [E2E Testing Guide](tests/e2e/README.md) | E2E testing with Playwright |
| [Testing Summary](tests/E2E_TESTING_SUMMARY.md) | Quick testing reference |

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 5.x, Python 3.12+
- **Database:** SQLite (dev) / PostgreSQL 16 (production)
- **ORM:** Django ORM
- **Admin:** Django Admin (built-in) untuk semua fungsi administratif
- **Task Queue:** Celery + Redis (report generation, notifikasi, kalkulasi analitik) *(target v2)*
- **Payment:** Midtrans / Xendit *(target v2)*

### Frontend
- **Template Engine:** Django Templates
- **CSS:** Tailwind CSS 3.4 + Flowbite
- **Interactivity:** HTMX 2.x
- **Charts:** Chart.js 4.x
- **Math Rendering:** KaTeX 0.16

### Infrastructure
- **App Server:** Passenger (Phusion)
- **Web Server:** Apache 2.4
- **Hosting:** Domainesia cPanel / Docker lokal
- **SSL:** Let's Encrypt

---

## 🧪 Testing

> Semua test dijalankan **di dalam container**: `docker compose exec web <perintah>`. Image harus berisi `requirements/development.txt` (pytest, pytest-django) agar test bisa jalan.

### Unit Testing
```bash
# Run all tests
docker compose exec web pytest

# Run with coverage
docker compose exec web pytest --cov=apps

# Run specific app tests
docker compose exec web pytest apps/questions/tests/
```

### E2E Testing (Playwright)
```bash
# Setup test data
docker compose exec web python manage.py setup_test_data

# Run all E2E tests
docker compose exec web pytest tests/e2e/ -v

# Run specific test category
docker compose exec web pytest tests/e2e/ -m student -v   # Student flow
docker compose exec web pytest tests/e2e/ -m parent -v    # Parent flow
docker compose exec web pytest tests/e2e/ -m quiz -v      # Quiz-related
```

### Testing Guidelines

**For functional testing** → Use Playwright E2E tests  
**For visual/UI review** → Use Antigravity browser feature

See [Testing Guidelines](.agent/TESTING_GUIDELINES.md) for detailed testing strategy.

**Test Documentation:**
- [E2E Testing Guide](tests/e2e/README.md)
- [Testing Summary](tests/E2E_TESTING_SUMMARY.md)
- [Testing Guidelines](.agent/TESTING_GUIDELINES.md)

**Test Credentials:**
- Parent: `orangtua` / `parent123`
- Student (Grade 4): `siswa4` / `siswa123`
- Admin: `admin` / `admin123`

---

## 📦 Import Soal

Bulk import soal menggunakan format JSON:

```bash
docker compose exec web python manage.py import_questions data/matematika-kelas6.json
```

Contoh format JSON:
```json
{
  "questions": [
    {
      "subject": "Matematika",
      "topic": "Pecahan",
      "grade": 6,
      "question_text": "Hasil dari 1/2 + 1/4 = ...",
      "question_type": "pilgan",
      "difficulty": "mudah",
      "options": ["A. 1/2", "B. 3/4", "C. 1/4", "D. 1"],
      "answer_key": "B",
      "explanation": "1/2 + 1/4 = 2/4 + 1/4 = 3/4",
      "tags": ["operasi-hitung", "pecahan-sederhana"],
      "kompetensi_dasar": ["3.1"],
      "estimated_time": 60,
      "points": 10
    }
  ]
}
```

---

## 🔐 Security

- CSRF protection enabled
- SQL injection prevention via Django ORM
- XSS prevention via template auto-escaping
- Password hashing (bcrypt)
- Role-based access control (RBAC)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat(scope): add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Fahri (Kaqfa)**

---

<div align="center">
Made with ❤️ for better learning experience
</div>
