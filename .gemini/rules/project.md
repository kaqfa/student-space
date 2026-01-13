# Bank Soal SD - Project Rules

## Project Context
Aplikasi learning management system untuk membantu orang tua mengajarkan anak SD. Menggunakan Django 5.0, PostgreSQL, Tailwind CSS, dan HTMX.

## Technology Stack
- **Backend:** Django 5.0, Python 3.11+
- **Database:** SQLite (dev) / PostgreSQL 15+ (production)
- **Frontend:** Django Templates, Tailwind CSS + Flowbite, HTMX
- **Testing:** pytest, pytest-django

## File Locations
- **Django Apps:** `apps/` directory
- **Settings:** `config/settings/` (base.py, development.py, production.py)
- **Templates:** `templates/`
- **Static Files:** `static/`
- **Documentation:** `docs/`

## Coding Conventions

### Python
- Use Black formatter (88 char line length)
- Use isort for import sorting
- Follow PEP 8
- Add type hints where applicable
- Write docstrings for classes and public methods

### Django
- Apps di dalam folder `apps/`
- Register apps dengan path `apps.<app_name>`
- Use class-based views (CBV) sebagai default
- Use Django ORM, hindari raw SQL
- Add proper `related_name` untuk ForeignKey/M2M

### Templates
- Use Django template language
- Reusable components di `templates/components/`
- HTMX partials di `templates/partials/`

### Database
- Use Django migrations exclusively
- Add indexes untuk frequently queried fields
- Use `select_related()` untuk FK
- Use `prefetch_related()` untuk M2M

## Environment & Dependencies
- **ALWAYS** use the virtual environment at `venv/`.
- Run python commands using `venv/bin/python` (Mac/Linux) or `venv\Scripts\python` (Windows), OR ensure `source venv/bin/activate` is run first.
- Only add explicitly required packages
- Do NOT use `pip freeze` for requirements
- Maintain separate requirements files: base.txt, development.txt, production.txt

## Testing
- Use pytest dan pytest-django
- Target coverage: >70%
- Test naming: `test_<functionality>`

## Important Documentation
- `docs/spec.md` - Technical specification
- `docs/prd.md` - Product requirements
- `docs/todo.md` - Development checklist
- `AGENTS.md` - AI agent guidelines

## Common Commands
```bash
# Development server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Tests
pytest

# Tailwind build
npm run build
```
