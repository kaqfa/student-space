# 📚 Student Space

<div align="center">

![Django](https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Flowbite](https://img.shields.io/badge/Flowbite-2.0-1C64F2?style=for-the-badge)

**Learning Management System untuk membantu orang tua mengajarkan anak SD dengan bank soal terstruktur dan analytics mendalam.**

</div>

---

## 🌟 Overview

Student Space adalah aplikasi berbasis web yang dirancang khusus untuk membantu orang tua dalam homeschooling anak SD (kelas 1-6). Aplikasi ini menyediakan bank soal terstruktur, sistem quiz dengan timer, progress tracking detail, dan analytics untuk mengidentifikasi kekuatan dan kelemahan pembelajaran anak.

## ✨ Fitur Utama

### 📝 Manajemen Bank Soal
- **Multi-tipe soal:** Pilihan ganda, Essay, dan Isian
- **Kategori bertingkat:** Subject → Topic → Question
- **Tagging system:** Skill-based, topic-based, difficulty-based
- **Kompetensi Dasar:** Mapping ke kurikulum nasional
- **Bulk import:** Import soal via JSON
- **LaTeX support:** Render rumus matematika dengan KaTeX

### 🎯 Quiz Engine
- **Practice Mode:** Tanpa timer, feedback langsung setelah jawab
- **Timed Quiz:** Dengan countdown timer
- **Custom Quiz:** Buat quiz spesifik untuk latihan terfokus
- **Randomisasi:** Acak urutan soal dan opsi jawaban

### 📊 Progress Tracking & Analytics
- **Per-topic tracking:** Lihat progress di setiap topik
- **Skill heatmap:** Visualisasi kekuatan & kelemahan per skill
- **KD coverage:** Track coverage kurikulum
- **Trend analysis:** Grafik perkembangan dari waktu ke waktu
- **Smart recommendations:** Identifikasi fokus area untuk improvement

### 👥 Multi-Role Access
- **Admin (Orang Tua):** Full control atas semua data
- **Pengajar (Tutor):** Manage assigned students
- **Student (Anak):** Akses quiz dan lihat progress sendiri

### 📱 Modern UI/UX
- **Responsive design:** Optimized untuk desktop, tablet, dan mobile
- **HTMX-powered:** Interaksi dinamis tanpa full page reload
- **Clean interface:** Fokus pada pembelajaran

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (untuk Tailwind CSS)
- PostgreSQL 15+ (optional, untuk production)

### Installation

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd bank_soal_project
   ```

2. **Create virtual environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit jika perlu custom settings
   # Default: SQLite database (no setup needed)
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Build Tailwind CSS**
   ```bash
   npm install
   npm run build
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Open browser**
   ```
   http://localhost:8000
   ```

---

## 📁 Project Structure

```
student-space/
├── apps/                    # Django applications
│   ├── accounts/           # User & authentication
│   ├── students/           # Student management
│   ├── subjects/           # Subjects & topics
│   ├── questions/          # Question bank
│   ├── quizzes/            # Quiz engine
│   ├── analytics/          # Progress tracking
│   └── core/               # Shared utilities
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
| [Technical Spec](docs/spec.md) | Detailed technical specification |
| [Product Requirements](docs/prd.md) | Product requirements document |
| [Todo List](docs/todo.md) | Development checklist |
| [Deployment Guide](docs/deployment-domainesia-passenger.md) | Panduan deploy Passenger (Docker & cPanel) |
| [AGENTS.md](AGENTS.md) | AI agent working guidelines |
| [Testing Guidelines](.agent/TESTING_GUIDELINES.md) | Testing strategy and best practices |
| [E2E Testing Guide](tests/e2e/README.md) | E2E testing with Playwright |
| [Testing Summary](tests/E2E_TESTING_SUMMARY.md) | Quick testing reference |

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 5.0
- **Database:** SQLite (dev) / PostgreSQL 15+ (production)
- **ORM:** Django ORM
- **Task Queue:** Celery (optional)
- **Cache:** Redis (optional)

### Frontend
- **Template Engine:** Django Templates
- **CSS:** Tailwind CSS 3.4 + Flowbite
- **Interactivity:** HTMX 1.9
- **Charts:** Chart.js 4.x
- **Math Rendering:** KaTeX 0.16

### Infrastructure
- **App Server:** Passenger (Phusion)
- **Web Server:** Apache 2.4
- **Hosting:** Domainesia cPanel / Docker lokal
- **SSL:** Let's Encrypt

---

## 🧪 Testing

### E2E Testing (Playwright)
```bash
# Setup test data
python manage.py setup_test_data

# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test category
pytest tests/e2e/ -m student -v    # Student flow tests
pytest tests/e2e/ -m parent -v     # Parent flow tests
pytest tests/e2e/ -m quiz -v       # Quiz-related tests

# Run with visible browser (for debugging)
pytest tests/e2e/ --headed -v

# Run specific test
pytest tests/e2e/test_student_flow.py::test_student_can_see_quiz_options -v
```

### Unit Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific app tests
pytest apps/questions/tests/
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
python manage.py import_questions data/matematika-kelas6.json
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
