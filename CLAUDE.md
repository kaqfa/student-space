# CLAUDE.md

Panduan kerja untuk Claude Code di repo **Ruang Belajar** (`student-space`).

> Panduan lengkap konvensi & arsitektur ada di **[AGENTS.md](AGENTS.md)** — baca itu terlebih dulu. File ini hanya merangkum hal paling kritis.

## Acuan dokumen

- **[docs/prd-v2.md](docs/prd-v2.md)** — PRD terbaru, sumber kebenaran arah produk (homeschooling SD–SMP + persiapan TKA).
- **[docs/v2-upgrade-plan.md](docs/v2-upgrade-plan.md)** — rencana upgrade backend/data model + **master sequence** (urutan kerja gabungan UI & backend).
- **[docs/ui-improvement-plan.md](docs/ui-improvement-plan.md)** — rencana redesign UI Orang Tua/Siswa + pemindahan fungsi admin ke Django Admin.
- `docs/prd.md`, `docs/spec.md` — dokumen v1 (SD only), historis.

## Yang wajib diingat

1. **Proyek berbasis Docker — JANGAN bikin virtualenv di repo ini.** Semua perintah (manage.py, pytest, migrate, seed, dll.) dijalankan **di dalam container** lewat `docker compose exec web ...`. Tidak ada `venv/`, `.venv`, atau pip install ke host. Lihat [§Perintah umum](#perintah-umum).
2. **Custom UI hanya untuk Orang Tua & Siswa.** Admin & Pengajar dilayani **Django Admin** (kustomisasi `ModelAdmin`/inline/actions). Jangan membangun custom UI admin baru; UI admin lama sedang dipindahkan ke Django Admin.
3. **Arah data model v2:** `Family` sebagai unit; `EducationLevel`/`Grade`/`AcademicYear`/`Enrollment` sebagai tabel; jenjang **SD + SMP**. Hindari menambah ketergantungan baru pada `grade` integer 1–6 atau model `Student` yang sudah deprecated.
4. **Mobile-first.** Mayoritas pengguna via smartphone.
5. **Stack:** Django 5.x + HTMX 2.x + Tailwind/Flowbite; PostgreSQL 16; deploy Apache + Passenger (DomaiNesia). Bukan Gunicorn/Nginx.

## Kondisi saat ini vs target v2

Codebase sekarang masih: SD kelas 1–6, `grade` integer, role `pengajar` digabung `parent`, belum ada modul `academic`/`tryouts`/`subscriptions`. Saat menambah fitur, selaraskan dengan PRD v2 dan catat gap-nya.

## Perintah umum

**Semua dijalankan di dalam container** (`web` service). Mulai stack: `docker compose --env-file .env.docker up -d` (lihat README untuk setup awal).

```bash
# Pola umum: docker compose exec web <perintah>
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py seed_initial_data        # groups+perms & academic seed (idempotent)
docker compose exec web pytest                                    # test
docker compose exec web pytest --cov=apps                         # test + coverage
docker compose exec web python manage.py import_questions data/<file>.json   # import soal
docker compose exec web bash                                      # shell ke container

# Build Tailwind (boleh di host, tooling Node):
npm run build                     # npm run watch untuk dev
```

> Dev server: container menjalankan Apache+Passenger otomatis (akses `http://localhost:8080`). Tidak perlu `runserver` manual di host.
> Catatan: image test harus berisi `requirements/development.txt` (pytest, pytest-django) agar `pytest` jalan di container.

## Git

- Commit convention: `<type>(<scope>): <subject>` (feat, fix, docs, refactor, test, chore).
- Branch fitur sesuai instruksi tugas; jangan push ke `main` tanpa izin.
