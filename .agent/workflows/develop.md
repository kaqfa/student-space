---
description: Standard development workflow for Bank Soal SD
---

# Development Workflow

## Starting Development Session

1. Activate virtual environment
```bash
source venv/bin/activate
```

2. Check current todo status
- Review `docs/todo.md` to see current progress
- Identify next task to work on

3. Start development server (if needed)
// turbo
```bash
./venv/bin/python manage.py runserver
```

## Creating New Django App

1. Create the app inside `apps/` directory
```bash
./venv/bin/python manage.py startapp <app_name> apps/<app_name>
```

2. Register in `INSTALLED_APPS` with path `apps.<app_name>`

3. Create models, views, forms, templates as needed

4. Create and run migrations
```bash
./venv/bin/python manage.py makemigrations <app_name>
./venv/bin/python manage.py migrate
```

## Adding New Feature

1. Create/update models if needed
```bash
./venv/bin/python manage.py makemigrations
./venv/bin/python manage.py migrate
```

2. Create views (prefer class-based views)

3. Create forms if needed

4. Create templates in `templates/<app_name>/`

5. Add URL patterns

6. Write tests

7. Update `docs/todo.md` to mark completed

## Running Tests

// turbo
```bash
./venv/bin/pytest
```

With coverage:
```bash
./venv/bin/pytest --cov=apps
```

## Building CSS

// turbo
```bash
npm run build
```

For watch mode during development:
```bash
npm run watch
```

## Committing Changes

Use conventional commit format:
```
<type>(<scope>): <subject>

Types: feat, fix, docs, style, refactor, test, chore
Scope: accounts, students, questions, quizzes, analytics, core
```

Example:
```bash
git add .
git commit -m "feat(questions): add bulk import functionality"
```
