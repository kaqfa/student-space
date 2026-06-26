# Ruang Belajar v2 — Implementation Progress

**Acuan:** [PRD v2](prd-v2.md) · [v2-upgrade-plan.md](v2-upgrade-plan.md) · [ui-improvement-plan.md](ui-improvement-plan.md)

Jalur kritis: **B0 → B1 → B2 → (B3∥B4) → (B5∥B6) → B7 → B8**
UI mengikuti: U0/U1 independen → U2 (setelah B1+B2) → U3 → U4 (setelah B5+B6) → U5 (setelah B7)

---

## Status Per Fase

| Fase | Lingkup | Status | Catatan |
|------|---------|--------|---------|
| **B0** | Celery+Redis prep, seed stub, baseline tests | ✅ Done | Celery feature-flagged via REDIS_URL; 0 unit tests (baseline); Django check clean |
| **U0** | Hapus custom UI admin, bersihkan nav, branding → "Ruang Belajar" | 🔄 In Progress | Agent berjalan |
| **U1** | Django Admin: ModelAdmin/inline/actions/permission groups | 🔄 In Progress | Agent berjalan |
| **B1** | App `academic`: EducationLevel, Grade, AcademicYear, GradeSubject; refactor grade:int→FK; KD→Topic; Enrollment | ⏳ Pending | Tunggu U0+U1 selesai; refactor 🔴 terbesar |
| **B2** | Family, ParentProfile, TutorProfile, role tutor; tautkan ParentStudent→Family | ⏳ Pending | Tunggu B1 |
| **U2** | Ganti user.grade→Enrollment di UI; year switcher; Family di dashboard | ⏳ Pending | Tunggu B1+B2 |
| **B3** | Question status (draft/published/archived), tipe benar/salah, QuestionSet, ImportBatch | ⏳ Pending | Bisa paralel dengan B4 setelah B1 |
| **B4** | Selaraskan Quiz→QuizConfig (mode practice/timed/custom, filter tag), status QuizSession | ⏳ Pending | Bisa paralel dengan B3 setelah B1 |
| **U3** | Redesign dashboard ortu (F-18) & siswa; perbaiki bug chart/link/aset; self-host assets | ⏳ Pending | Tunggu U2 |
| **B5** | App `tryouts`: ExamBlueprint, ExamSection, TryoutSession, TryoutSectionScore, StudyPlan, StudyPlanItem, ExamTarget | ⏳ Pending | Tunggu B1+B4; additive |
| **B6** | App `analytics` lanjutan: ProgressSnapshot, MasteryRecord, Celery batch jobs | ⏳ Pending | Bisa paralel dengan B5 setelah B1+B4 |
| **U4** | UI Try-out, Readiness/Countdown, Study Plan, Riwayat lintas tahun, Laporan PDF | ⏳ Pending | Tunggu B5+B6 |
| **B7** | App `subscriptions`: Plan, PlanFeature, Subscription, Invoice, PaymentTransaction + middleware feature gating + webhook | ⏳ Pending | Tunggu B2 |
| **U5** | Plan badge, gating halus, pricing page, landing page | ⏳ Pending | Tunggu B7 |
| **B8** | Cleanup: hapus model Student lama, grade:int columns, shim deprecated | ⏳ Pending | Contract terakhir, tunggu semua di atas |

---

## Detail B0 (✅ Done)

**Files created/modified:**
- `config/settings/base.py` — Celery config block (feature-flagged via REDIS_URL)
- `config/celery.py` — Celery app setup untuk `ruang_belajar`
- `config/__init__.py` — guarded import celery app
- `requirements/base.txt` — tambah `celery>=5.3`, `redis>=5.0`, `django-celery-results>=2.5`
- `apps/core/management/__init__.py` + `commands/__init__.py` — created
- `apps/core/management/commands/seed_initial_data.py` — stub: buat 3 Django groups (content_manager, user_manager, finance), idempotent
- `docs/test-baseline-b0.md` — baseline snapshot

**Temuan:** Django check bersih. Tidak ada unit tests (hanya Playwright E2E, tidak installed). Baseline: 0 unit tests.

---

## Konteks Teknis Penting

- **Docker:** `docker compose up -d db` untuk DB. Web container (Passenger) gagal pull image (TLS timeout) — gunakan `python manage.py runserver` untuk dev
- **DB:** SQLite untuk dev (default), PostgreSQL via env var `DATABASE_URL`
- **Settings:** `config.settings.base` (paling clean), `config.settings.development` (perlu debug_toolbar di venv)
- **Stack:** Django 5.x + HTMX 2.x + Tailwind/Flowbite + PostgreSQL 16 + Apache + Passenger (prod)
- **Deploy:** Docker volume mount — edit file langsung di disk, otomatis reflect di container

## Keputusan Desain Kunci (dari v2-upgrade-plan.md §3)

1. **StudentProfile:** Pertahankan `User(role=student)` — jangan pecah ke tabel baru (risiko tinggi migrasi FK)
2. **grade:int → Grade FK:** Pakai expand-contract (3 langkah: expand → migrate → contract)
3. **KD → Topic:** Tambah `topic = FK(Topic, null=True)`, backfill, jadikan sumber utama
4. **QuestionOption:** Tetap JSONField kecuali ada kebutuhan nyata

## Apps Existing (v1)

| App | Models |
|-----|--------|
| `accounts` | User (custom), ParentStudent |
| `subjects` | Subject, Topic |
| `questions` | Question, Tag, KompetensiDasar |
| `quizzes` | Quiz, QuizSession |
| `analytics` | Attempt |
| `students` | Student (deprecated, tidak ada FK aktif) |
| `core` | (kosong, utils) |

## Apps Baru (v2)

- `academic` — EducationLevel, Grade, Subject (relasi), GradeSubject, Topic (relasi), Competency, AcademicYear, Enrollment
- `tryouts` — ExamBlueprint, ExamSection, TryoutSession, TryoutSectionScore, StudyPlan, StudyPlanItem, ExamTarget
- `subscriptions` — Plan, PlanFeature, Subscription, Invoice, PaymentTransaction

---

*Update file ini setiap fase selesai.*
