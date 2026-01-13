# AGENTS.md - Bank Soal SD

## Project Overview

Bank Soal SD adalah aplikasi learning management system berbasis Django untuk membantu orang tua mengajarkan anak SD (kelas 1-6) dengan bank soal terstruktur, progress tracking detail, dan analytics mendalam untuk mengidentifikasi kekuatan dan kelemahan pembelajaran.

### Core Value Proposition

- Progress tracking detail per kompetensi dan tag
- Advanced analytics untuk identifikasi learning gaps
- Quiz mode dengan timer untuk latihan terfokus
- Multi-role access (admin/pengajar/anak)
- Bulk import soal via JSON untuk efisiensi content creation

---

## Technology Stack

### Backend

- **Framework:** Django 5.0.x
- **Language:** Python 3.11+
- **Database:** SQLite (development) / PostgreSQL 15+ (production)
- **ORM:** Django ORM

### Frontend

- **Template Engine:** Django Templates
- **CSS Framework:** Tailwind CSS 3.4.x + Flowbite (components)
- **JavaScript:** HTMX 1.9.x (dynamic interactions)
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
│   ├── accounts/        # User management, authentication
│   ├── students/        # Student management
│   ├── subjects/        # Subjects & Topics
│   ├── questions/       # Questions, Tags, KD
│   ├── quizzes/         # Quiz sessions & logic
│   ├── analytics/       # Progress tracking & reporting
│   └── core/            # Shared utilities
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

### 2. Role-based Access Control

Tiga role utama:

- **Admin (Orang Tua):** Full access
- **Pengajar (Tutor):** Read/write assigned students
- **Student (Anak):** Own data only

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

| File                      | Description                     |
| ------------------------- | ------------------------------- |
| `docs/spec.md`            | Technical specification lengkap |
| `docs/prd.md`             | Product requirements document   |
| `docs/todo.md`            | Development todo/checklist      |
| `config/settings/base.py` | Base Django settings            |
| `requirements/base.txt`   | Python dependencies             |

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

- VPS (Domainesia/DigitalOcean)
- Gunicorn + Nginx
- PostgreSQL
- Let's Encrypt SSL

Lihat `docs/spec.md` Section 5 untuk detail deployment.
