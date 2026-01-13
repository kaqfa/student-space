---
description: How to setup development environment for Bank Soal SD
---

# Development Environment Setup

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Tailwind CSS)
- PostgreSQL 15+ (optional, only for production-like setup)

## Quick Start (SQLite - Recommended for Development)

### Step 1: Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### Step 2: Install Python Dependencies

// turbo
```bash
./venv/bin/pip install -r requirements/development.txt
```

### Step 3: Run Migrations

// turbo
```bash
./venv/bin/python manage.py migrate
```

### Step 4: Create Superuser

```bash
./venv/bin/python manage.py createsuperuser
```

### Step 5: Setup Tailwind CSS

// turbo
```bash
npm install
npm run build
```

### Step 6: Run Development Server

// turbo
```bash
./venv/bin/python manage.py runserver
```

### Step 7: Verify

Open browser and navigate to:
- http://localhost:8000 - Main site
- http://localhost:8000/admin - Admin panel

---

## PostgreSQL Setup (Optional - For Production-like Environment)

If you want to test with PostgreSQL locally:

### Step 1: Create Database

```bash
sudo -u postgres psql
```

In psql:
```sql
CREATE DATABASE banksoal_dev;
CREATE USER banksoal WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE banksoal_dev TO banksoal;
\q
```

### Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:
```
DATABASE_ENGINE=postgresql
DATABASE_NAME=banksoal_dev
DATABASE_USER=banksoal
DATABASE_PASSWORD=dev_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Step 3: Run Migrations

```bash
./venv/bin/python manage.py migrate
```

---

## Common Issues

### Tailwind Not Working
- Run `npm run build` to compile CSS
- Check if `static/css/output.css` is generated
- Clear browser cache

### SQLite Database Locked
- This can happen with concurrent access
- Restart development server
- For heavy testing, consider using PostgreSQL

### Permission Error on Mac with PostgreSQL
- Ensure PostgreSQL service is running
- Try connecting with: `psql postgres`
