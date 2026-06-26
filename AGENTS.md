# AGENTS.md - Ruang Belajar

> **Acuan produk:** [docs/prd-v2.md](docs/prd-v2.md) adalah PRD terbaru dan menjadi sumber kebenaran arah produk. Dokumen ini (AGENTS.md) menjelaskan konvensi kerja & kondisi codebase saat ini. Untuk rencana penyelarasan UI lihat [docs/ui-improvement-plan.md](docs/ui-improvement-plan.md).

## Project Overview

Ruang Belajar (codebase: `student-space`) adalah platform homeschooling & persiapan ujian (TKA) berbasis Django untuk jenjang **SD–SMP**. Menyediakan bank soal terstruktur, kuis & try-out simulasi, pelacakan progress lintas tahun ajaran, dan analitik mendalam.

> **Catatan kondisi saat ini vs target v2:** basis kode sekarang masih SD (kelas 1–6), `grade` sebagai integer, role `pengajar` digabung ke `parent`, dan belum ada modul `academic`/`tryouts`/`subscriptions`. PRD v2 menargetkan: `Family` sebagai unit, `Grade`/`AcademicYear`/`Enrollment` sebagai tabel, jenjang SMP, serta modul try-out & subscription. Saat menambah fitur, ikuti arah v2.

### Core Value Proposition

- Progress tracking detail per kompetensi dan tag
- Try-out simulasi (TKA) + readiness score + study plan otomatis *(target v2)*
- Advanced analytics untuk identifikasi learning gaps, termasuk lintas tahun ajaran
- Multi-role: **Admin & Pengajar via Django Admin**, **Orang Tua & Siswa via custom UI**
- Bulk import soal via JSON untuk efisiensi content creation
- Monetisasi freemium (Free/Basic/Pro) dengan feature gating *(target v2)*

---

## Technology Stack

### Backend

- **Framework:** Django 5.x
- **Language:** Python 3.12+
- **Database:** SQLite (development) / PostgreSQL 16 (production)
- **ORM:** Django ORM
- **Admin:** Django Admin (built-in) — satu-satunya interface untuk Admin & Pengajar
- **Task Queue:** Celery + Redis *(target v2)*
- **Payment:** Midtrans / Xendit *(target v2)*

### Frontend

- **Template Engine:** Django Templates
- **CSS Framework:** Tailwind CSS 3.4.x + Flowbite (components)
- **JavaScript:** HTMX 2.x (dynamic interactions)
- **Charts:** Chart.js 4.x
- **Math Rendering:** KaTeX 0.16.x

### Design Principles
- **Mobile-first:** Responsive design prioritizing mobile experience
- **Clean UI:** Minimalist, fokus pada content
- **Flowbite Components:** Gunakan Flowbite untuk UI components (cards, modals, forms, etc.)

### Development Tools

- **Code Quality:** Black, Flake8, isort
- **Testing:** pytest, pytest-django

---

## Project Structure

```
bank_soal_project/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/        # User, auth, role; (target v2: Family, ParentProfile, TutorProfile)
│   ├── students/        # DEPRECATED — student kini = User(role=student) + ParentStudent
│   ├── subjects/        # Subjects & Topics (target v2: pindah ke app `academic`)
│   ├── questions/       # Questions, Tags, KD
│   ├── quizzes/         # Quiz config & sessions
│   ├── analytics/       # Attempt, progress tracking & reporting
│   └── core/            # Shared utilities
│   # Target v2 (belum ada):
│   # ├── academic/      # EducationLevel, Grade, AcademicYear, Enrollment, GradeSubject
│   # ├── tryouts/       # ExamBlueprint, ExamSection, TryoutSession, StudyPlan, ExamTarget
│   # └── subscriptions/ # Plan, PlanFeature, Subscription, Invoice, PaymentTransaction
├── templates/
├── static/
├── media/
└── docs/
```

---

## Django Apps

### 1. accounts

- Custom User model (extends AbstractUser)
- Role-based permissions: `admin`, `pengajar`, `student`
- Login/logout views
- Profile management

### 2. students

- Student CRUD
- Student-pengajar assignment
- Student profile page

### 3. subjects

- Subject & Topic CRUD
- Hierarchical display

### 4. questions

- Question CRUD dengan support untuk: `pilgan`, `essay`, `isian`
- Tag management (skill, topic, difficulty, custom)
- Kompetensi Dasar (KD) management
- Bulk import via JSON

### 5. quizzes

- Quiz creation & configuration
- Quiz types: `practice`, `timed`, `custom`
- Quiz-taking interface (HTMX-powered)
- Timer logic

### 6. analytics

- Attempt recording
- Metrics calculation
- Progress dashboard
- Report generation (PDF/CSV)

### 7. core

- Shared utilities
- Mixins & decorators
- Constants

---

## Coding Conventions

### Python/Django

- Follow PEP 8 style guide
- Use Black formatter with default settings
- Use isort for import sorting
- Maximum line length: 88 characters (Black default)
- Use type hints where applicable
- Write docstrings for all classes and public methods

### Naming Conventions

- **Models:** PascalCase (`QuizSession`, `KompetensiDasar`)
- **Views:** PascalCase with suffix (`StudentListView`, `QuizTakeView`)
- **Functions:** snake_case (`calculate_accuracy`, `get_remaining_time`)
- **Variables:** snake_case (`quiz_session`, `total_score`)
- **URLs:** kebab-case (`/quiz-sessions/`, `/kompetensi-dasar/`)
- **Templates:** snake_case dengan slash (`students/list.html`, `quizzes/take.html`)

### Database

- Use Django migrations exclusively
- Add proper indexes for frequently queried fields
- Use meaningful related_name for ForeignKey/ManyToMany

### Templates

- Use Django template language (not Jinja2)
- Create reusable components in `templates/components/`
- Use HTMX partials in `templates/partials/`
- Follow BEM-like naming for CSS classes

### JavaScript

- Minimal vanilla JS (prefer HTMX for interactions)
- Use ES6+ syntax
- Keep scripts in `static/js/`

---

## Key Design Decisions

### 1. HTMX over SPA Framework

Menggunakan HTMX untuk dynamic interactions daripada React/Vue karena:

- Simpler architecture (Django monolith)
- Faster development
- SEO-friendly
- Perfect for this use case

### 2. Role-based Access Control & Pembagian Interface

Empat role (PRD v2 §3.1, §8.1):

- **Admin:** Pengelola platform — **hanya via Django Admin** (konten, user, konfigurasi). Tidak ada custom UI admin.
- **Orang Tua:** **Custom UI** — kelola anak, pantau progress, kelola langganan.
- **Pengajar (opsional):** **Django Admin terbatas** (permission group) — siswa yang di-assign + buat kuis.
- **Siswa:** **Custom UI** — mengerjakan kuis/try-out & lihat progress sendiri.

**Aturan penting:** Custom UI (Django Templates + HTMX) dibangun **hanya** untuk Orang Tua & Siswa. Semua fungsi admin/pengajar dilayani Django Admin dengan kustomisasi `ModelAdmin`/inline/actions. Custom UI admin yang masih ada (bank soal CRUD, dll.) sedang dipindahkan ke Django Admin — lihat [docs/ui-improvement-plan.md](docs/ui-improvement-plan.md).

### 3. Tagging System

Flexible tagging dengan categories:

- `skill`: problem-solving, calculation, etc.
- `topic`: pecahan, geometri, etc.
- `difficulty`: basic, intermediate, advanced
- `custom`: user-defined

### 4. Kompetensi Dasar (KD)

Mapping ke kurikulum nasional untuk tracking coverage.

---

## Common Tasks

### Running Development Server
```bash
./venv/bin/python manage.py runserver
```

### Running Tests
```bash
./venv/bin/pytest
./venv/bin/pytest --cov=apps  # with coverage
```

### Running Migrations
```bash
./venv/bin/python manage.py makemigrations
./venv/bin/python manage.py migrate
```

### Building Tailwind CSS

```bash
npm run build
# atau untuk watch mode:
npm run watch
```

### Importing Questions from JSON
```bash
./venv/bin/python manage.py import_questions data/matematika-kelas6.json
```

---

## Important Files

| File                            | Description                                  |
| ------------------------------- | -------------------------------------------- |
| `docs/prd-v2.md`                | **PRD terbaru (acuan utama)**                |
| `docs/ui-improvement-plan.md`   | Rencana redesign UI + migrasi ke Django Admin |
| `docs/spec.md`                  | Technical specification lengkap (v1)         |
| `docs/prd.md`                   | PRD lama (SD only) — historis                |
| `docs/todo.md`                  | Development todo/checklist                   |
| `config/settings/base.py`       | Base Django settings                         |
| `requirements/base.txt`         | Python dependencies                          |

---

## Development Workflow

### 1. Creating New Feature

1. Check `docs/todo.md` untuk task yang akan dikerjakan
2. Create/update models jika diperlukan
3. Create/update migrations
4. Create views, forms, templates
5. Add URL patterns
6. Write tests
7. Update documentation

### 2. Adding New Django App
```bash
./venv/bin/python manage.py startapp <app_name> apps/<app_name>
```

Kemudian register di `INSTALLED_APPS` dengan path `apps.<app_name>`.

### 3. Commit Convention

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scope: accounts, students, questions, quizzes, analytics, core
```

---

## Testing Strategy

### Unit Tests

- Test models (validations, methods, properties)
- Test forms (validation, cleaning)
- Test utility functions

### Integration Tests

- Test views with request/response
- Test complete user flows

### Target Coverage

- Minimum 70% code coverage

---

## Security Guidelines

- Use Django's built-in CSRF protection
- Never expose sensitive data in templates
- Validate all user inputs
- Use Django ORM (no raw SQL)
- Implement proper permission checks
- Sanitize file uploads

---

## Performance Guidelines

- Use `select_related()` untuk ForeignKey
- Use `prefetch_related()` untuk ManyToMany
- Add database indexes untuk frequently queried fields
- Cache expensive analytics calculations (optional Redis)
- Optimize images on upload

---

## Deployment

Target deployment:

- VPS / shared hosting (Domainesia cPanel)
- **Apache + Phusion Passenger** (bukan Gunicorn/Nginx) agar kompatibel dengan stack DomaiNesia
- Docker untuk simulasi lokal & production (app + db + redis + worker)
- PostgreSQL 16
- Let's Encrypt SSL

Lihat `docs/deployment-domainesia-passenger.md` dan `README.md` untuk detail deployment.
