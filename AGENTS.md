# AGENTS.md - Ruang Belajar

> **Acuan produk:** [docs/prd-v2.md](docs/prd-v2.md) adalah PRD terbaru dan menjadi sumber kebenaran arah produk. Dokumen ini (AGENTS.md) menjelaskan konvensi kerja & kondisi codebase saat ini. Untuk rencana penyelarasan UI lihat [docs/ui-improvement-plan.md](docs/ui-improvement-plan.md).

> **⚙️ Proyek berbasis Docker.** Semua perintah (manage.py, pytest, migrate, seed, shell) dijalankan **di dalam container** via `docker compose exec web <perintah>`. **Jangan** membuat virtualenv (`venv/`, `.venv`) di repo ini atau pip install ke host. Lihat [§Common Tasks](#common-tasks).

## Project Overview

Ruang Belajar (codebase: `student-space`) adalah platform homeschooling & persiapan ujian (TKA) berbasis Django untuk jenjang **SD–SMP**. Menyediakan bank soal terstruktur, kuis & try-out simulasi, pelacakan progress lintas tahun ajaran, dan analitik mendalam.

> **Catatan kondisi saat ini vs target v2 (progress di [docs/implementation-progress.md](docs/implementation-progress.md)):**
> - **Sudah jalan (B0–B2, U0):** app `academic` (`EducationLevel`/`Grade`/`AcademicYear`/`GradeSubject`/`Enrollment`); `Family` + `FamilyMembership` (M2M), `ParentProfile`/`TutorProfile`, role `tutor`; `grade_ref` FK nullable sudah di-backfill di User/Subject/KD/Quiz/QuizSession (KD→Topic); custom UI admin sudah dihapus (admin via Django Admin).
> - **Masih transisi:** kolom `grade` integer 1–6 **masih ada** berdampingan dengan `grade_ref` (contract/drop ditunda ke fase B8); UI ortu/siswa masih baca `user.grade` (rewire ke `Enrollment` = fase U2).
> - **Belum ada:** modul `tryouts`/`subscriptions`, analytics lanjutan (B3+).
>
> Saat menambah fitur: pakai `grade_ref`/`Enrollment`, bukan `grade` integer; jangan tambah dependensi baru ke `grade:int` atau model `Student` deprecated.

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
│   ├── accounts/        # User+role(admin/parent/student/tutor), ParentStudent, Family, FamilyMembership, ParentProfile, TutorProfile
│   ├── academic/        # EducationLevel, Grade, AcademicYear, GradeSubject, Enrollment
│   ├── students/        # DEPRECATED — student kini = User(role=student) + ParentStudent
│   ├── subjects/        # Subjects & Topics (punya grade_ref FK ke academic.Grade)
│   ├── questions/       # Questions, Tags, KD (KD→Topic + grade_ref)
│   ├── quizzes/         # Quiz config & sessions (grade_ref)
│   ├── analytics/       # Attempt, progress tracking & reporting
│   └── core/            # Shared utilities, seed_initial_data command
│   # Target v2 (belum ada):
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
- Role-based permissions: `admin`, `parent`, `student`, `tutor` (alias lama `is_pengajar_or_admin` masih ada, deprecated)
- `Family` + `FamilyMembership` (M2M, unit/tenancy root), `ParentProfile`/`TutorProfile` (thin)
- `ParentStudent` link + workflow verifikasi (tertaut ke `Family`)
- Login/logout views, profile management

### 2. academic

- `EducationLevel` (SD/SMP), `Grade` (kelas 1–9), `AcademicYear`, `GradeSubject` (M2M), `Enrollment` (Student×Grade×Year)
- Sumber "kelas saat ini" via `User.current_enrollment` (gantikan `user.grade` integer)
- Seed reference data idempotent: `python manage.py seed_initial_data`

### 3. students

- (DEPRECATED) Model `Student` lama — tidak dipakai; student = `User(role=student)` + `ParentStudent`
- Dihapus penuh di fase B8

### 4. subjects

- Subject & Topic CRUD (Subject punya `grade_ref` FK ke `academic.Grade`)
- Hierarchical display

### 5. questions

- Question CRUD dengan support untuk: `pilgan`, `essay`, `isian` (target v2: tambah `benar/salah` + field `status`)
- Tag management (skill, topic, difficulty, custom)
- Kompetensi Dasar (KD) management (KD→Topic via FK)
- Bulk import via JSON (CLI `import_questions` + admin action "Import JSON" di `QuestionAdmin`)

### 6. quizzes

- Quiz creation & configuration
- Quiz types: `practice`, `timed`, `custom`
- Quiz-taking interface (HTMX-powered)
- Timer logic

### 7. analytics

- Attempt recording
- Metrics calculation
- Progress dashboard
- Report generation (PDF/CSV)

### 8. core

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

> **Semua perintah Python/Django dijalankan di dalam container** (`web` service), pola: `docker compose exec web <perintah>`. Mulai stack: `docker compose --env-file .env.docker up -d` (lihat README). Jangan bikin venv di host.

### Development Server
Container menjalankan Apache+Passenger otomatis → akses `http://localhost:8080`. Tidak ada `runserver` manual di host.

### Running Tests
```bash
docker compose exec web pytest
docker compose exec web pytest --cov=apps   # with coverage
```
> Image test harus berisi `requirements/development.txt` (pytest, pytest-django) agar test jalan di container.

### Running Migrations & Seed
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_initial_data   # groups+perms & academic reference (idempotent)
```

### Building Tailwind CSS
```bash
npm run build   # tooling Node, boleh di host; npm run watch untuk dev
```

### Importing Questions from JSON
```bash
docker compose exec web python manage.py import_questions data/matematika-kelas6.json
```

---

## Important Files

| File                            | Description                                  |
| ------------------------------- | -------------------------------------------- |
| `docs/prd-v2.md`                | **PRD terbaru (acuan utama)**                |
| `docs/v2-upgrade-plan.md`       | Rencana upgrade backend + master sequence    |
| `docs/ui-improvement-plan.md`   | Rencana redesign UI + migrasi ke Django Admin |
| `docs/implementation-progress.md` | **Status fase B0–B8 / U0–U5 terkini**      |
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
docker compose exec web python manage.py startapp <app_name> apps/<app_name>
```

Kemudian register di `INSTALLED_APPS` dengan path `apps.<app_name>`.

### 3. Commit Convention

```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scope: accounts, academic, subjects, questions, quizzes, analytics, core
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
