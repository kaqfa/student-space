# CLAUDE.md

Panduan kerja untuk Claude Code di repo **Ruang Belajar** (`student-space`).

> Panduan lengkap konvensi & arsitektur ada di **[AGENTS.md](AGENTS.md)** — baca itu terlebih dulu. File ini hanya merangkum hal paling kritis.

## Acuan dokumen

- **[docs/prd-v2.md](docs/prd-v2.md)** — PRD terbaru, sumber kebenaran arah produk (homeschooling SD–SMP + persiapan TKA).
- **[docs/v2-upgrade-plan.md](docs/v2-upgrade-plan.md)** — rencana upgrade backend/data model + **master sequence** (urutan kerja gabungan UI & backend).
- **[docs/ui-improvement-plan.md](docs/ui-improvement-plan.md)** — rencana redesign UI Orang Tua/Siswa + pemindahan fungsi admin ke Django Admin.
- `docs/prd.md`, `docs/spec.md` — dokumen v1 (SD only), historis.

## Yang wajib diingat

1. **Custom UI hanya untuk Orang Tua & Siswa.** Admin & Pengajar dilayani **Django Admin** (kustomisasi `ModelAdmin`/inline/actions). Jangan membangun custom UI admin baru; UI admin lama sedang dipindahkan ke Django Admin.
2. **Arah data model v2:** `Family` sebagai unit; `EducationLevel`/`Grade`/`AcademicYear`/`Enrollment` sebagai tabel; jenjang **SD + SMP**. Hindari menambah ketergantungan baru pada `grade` integer 1–6 atau model `Student` yang sudah deprecated.
3. **Mobile-first.** Mayoritas pengguna via smartphone.
4. **Stack:** Django 5.x + HTMX 2.x + Tailwind/Flowbite; PostgreSQL 16; deploy Apache + Passenger (DomaiNesia). Bukan Gunicorn/Nginx.

## Kondisi saat ini vs target v2

Codebase sekarang masih: SD kelas 1–6, `grade` integer, role `pengajar` digabung `parent`, belum ada modul `academic`/`tryouts`/`subscriptions`. Saat menambah fitur, selaraskan dengan PRD v2 dan catat gap-nya.

## Perintah umum

```bash
python manage.py runserver        # dev server
python manage.py makemigrations && python manage.py migrate
pytest                            # test
pytest --cov=apps                 # test + coverage
npm run build                     # build Tailwind (npm run watch untuk dev)
python manage.py import_questions data/<file>.json   # import soal
```

## Git

- Commit convention: `<type>(<scope>): <subject>` (feat, fix, docs, refactor, test, chore).
- Branch fitur sesuai instruksi tugas; jangan push ke `main` tanpa izin.
