# Ruang Belajar v2 — Implementation Progress

**Acuan:** [PRD v2](prd-v2.md) · [v2-upgrade-plan.md](v2-upgrade-plan.md) · [ui-improvement-plan.md](ui-improvement-plan.md)

Jalur kritis: **B0 → B1 → B2 → (B3∥B4) → (B5∥B6) → B7 → B8**
UI mengikuti: U0/U1 independen → U2 (setelah B1+B2) → U3 → U4 (setelah B5+B6) → U5 (setelah B7)

---

## Status Per Fase

| Fase | Lingkup | Status | Catatan |
|------|---------|--------|---------|
| **B0** | Celery+Redis prep, seed stub, baseline tests | ✅ Done | Celery feature-flagged via REDIS_URL; 0 unit tests (baseline); Django check clean |
| **U0** | Hapus custom UI admin, bersihkan nav, branding → "Ruang Belajar" | ✅ Done | Lihat detail di bawah |
| **U1** | Django Admin: ModelAdmin/inline/actions/permission groups | ✅ Done | Import JSON action + permission groups; lihat detail di bawah |
| **B1** | App `academic`: EducationLevel, Grade, AcademicYear, GradeSubject; refactor grade:int→FK; KD→Topic; Enrollment | ✅ Done | Expand+migrate (contract ditunda B8); lihat detail di bawah |
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

## Detail U0 (✅ Done)

Menghapus seluruh custom UI admin; fungsi admin sekarang hanya via Django Admin (`/admin/`). Tidak menyentuh model/migrasi.

**URL/View dihapus:**
- `questions`: `urls.py` & `views.py` dikosongkan (list/create/detail/update/delete, import, tag-* CRUD, kd-* CRUD).
- `quizzes`: dihapus `QuizListView/CreateView/UpdateView/DetailView/DeleteView/QuizQuestionAddView/QuizQuestionRemoveView` + URL `list/create/detail/update/delete/question-add/question-remove`. **Tetap**: `student-list`, `take_quiz`, `save_answer`, `result`, `proxy_select`, `create_subject_quiz`, `create_custom_quiz`.
- `analytics`: dihapus `AdminAnalyticsDashboardView`, `StudentAttemptHistoryView`, `TagAnalyticsView`, `KDCoverageView`, `ExportStudentReportView`, `ExportClassSummaryView` + URL terkait. **Tetap**: `progress`, `api-accuracy-trend`.
- `students`: dihapus `StudentListView` deprecated (model `Student` lama) + URL `list/`.
- `core`: dihapus `AdminDashboardView` (tidak ter-route); fallback redirect `DashboardView` diubah dari `analytics:dashboard` → `/admin/`.

**Template dihapus (25 file):** `questions/{list,form,detail,confirm_delete,import,tag_list,tag_form,tag_confirm_delete,kd_list,kd_form,kd_confirm_delete}.html`, `quizzes/{list,form,detail,confirm_delete,add_questions}.html`, `analytics/{admin_dashboard,tag_heatmap,kd_coverage,attempt_history}.html`, `students/{list,form,confirm_delete,detail}.html`, `admin/questions/question_changelist.html`, `core/dashboard.html`.

**Admin:** `QuestionAdmin.change_list_template` (override untuk tombol import custom) dihapus. `quiz_changelist.html` **dipertahankan** karena hanya menaut ke view parent yang tetap ada (`create_subject_quiz`/`create_custom_quiz`); penataan ulang penuh Django Admin masuk U1.

**Navigasi:**
- `navbar.html`: link admin (Bank Soal/Tags/KD/Kuis/Siswa/Analytics) diganti satu link **"Admin Panel" → /admin/** (kondisi `is_admin or is_superuser`). Berhenti memakai `is_pengajar_or_admin`.
- `sidebar.html`: seluruh blok `{% if user.is_admin %}` (Materi & Soal, Aktivitas) dihapus; menu parent kini di bawah `{% if user.is_parent %}`. Sidebar hanya melayani Orang Tua & Siswa.

**Branding:** seluruh "Bank Soal SD" → "Ruang Belajar" (24 file). Grep `Bank Soal` di `templates/` = 0.

**Tests:** kelas test yang menargetkan view yang dihapus dibuang (`questions/tests/test_views.py` dikosongkan; admin/export/student-history di `analytics`; `TestQuizCRUDViews` di `quizzes`).

**Verifikasi:** `manage.py check` (settings `config.settings.base`) bersih, 0 issues. Semua URL yang dipertahankan reverse OK; URL yang dihapus tidak lagi resolve (tidak ada `NoReverseMatch` dangling). `navbar.html` & `sidebar.html` render tanpa error.

> Catatan env: settings default `config.settings.development` butuh `debug_toolbar` (belum terpasang di venv ini) — gunakan `DJANGO_SETTINGS_MODULE=config.settings.base` untuk `check`.

---

## Detail U1 (✅ Done)

Django Admin sudah substansial sejak v1 (ModelAdmin/filter/search/inline/actions untuk User, ParentStudent, Attempt, Tag, KD, Question, Quiz, Subject, Topic). U1 menutup gap yang tersisa dari ui-improvement-plan §5.4:

- **Import JSON (F-08):** `QuestionAdmin` dapat tombol **"Import JSON"** di changelist (`templates/admin/questions/question_changelist.html`) → view `import_json_view` via `get_urls()` (`apps/questions/admin.py`). Reuse service `import_questions_from_json` (sudah ada), reuse `QuestionImportForm` (field `file`). Template form: `templates/admin/questions/question_import.html`.
- **Permission groups (F-23):** `seed_initial_data` kini assign permission ke 3 group (idempotent, defensif terhadap model yang belum ada):
  - `content_manager`: add/change/view Question, Tag, KD, Subject, Topic, Quiz + academic content (30 perms)
  - `user_manager`: User, ParentStudent, Enrollment (9 perms)
  - `finance`: stub kosong (diisi B7)
- **Out of scope (sengaja):** bulk publish/archive butuh Question.status → B3.

## Detail B1 (✅ Done — expand + migrate)

App baru `apps/academic`. Strategi expand+migrate; kolom `grade:int` lama **tetap** (contract = B8). UI rewire `user.grade`→Enrollment **tidak** dilakukan di sini (= U2).

**Models** (`apps/academic/models.py`): `EducationLevel` (SD/SMP), `Grade` (FK level, number 1–9, unique (level,number)), `AcademicYear` (unique name, single-active enforced di `save()`), `GradeSubject` (M2M Grade×Subject, unique), `Enrollment` (student×grade×year, unique (student,year), status active/completed).

**Expand** (`grade_ref = FK(academic.Grade, null=True, SET_NULL)` ditambahkan ke): `accounts.User`, `subjects.Subject`, `questions.KompetensiDasar`, `quizzes.Quiz`, `quizzes.QuizSession`. Plus `questions.KompetensiDasar.topic = FK(subjects.Topic, null=True)` (KD→Topic, §3.3 — backfill ditunda, admin reassign).

**Migrate** (`apps/academic/migrations/0002_backfill.py`, reversible): seed EducationLevel+Grade (SD 1–6, SMP 7–9) + default AcademicYear "2025/2026" (active), backfill `grade_ref` dari `grade:int` di 5 model, backfill `Enrollment` untuk tiap `User(role=student)` dengan grade. Seed logic di `apps/academic/seed.py` (dipakai migration + `seed_initial_data`, idempotent).

**Helper:** `User.current_enrollment` property → active Enrollment untuk active year (atau None).

**Admin** (`apps/academic/admin.py`): 5 model + GradeSubject inline di Grade, GradeInline di EducationLevel, autocomplete_fields.

**Verifikasi:** `manage.py check` bersih; `makemigrations --check` = "No changes detected"; migrate dari DB kosong OK + seed benar (2 level, 9 grade, 1 active year); backfill migration reversible (unapply/reapply OK). **120 tests pass** (suite lama + baru, tanpa regresi) — dijalankan via venv `.venv-test` (Django 5.0.14 + pytest-django, settings `config.settings.development`).

> Catatan env: `python3` sistem = Django 6.0.5 tanpa pytest-django/debug_toolbar → untuk manage.py pakai `DJANGO_SETTINGS_MODULE=config.settings.base`. Untuk pytest dibuat venv `.venv-test` (gitignored) dari `requirements/development.txt` + `playwright` (dibutuhkan `tests/conftest.py`).

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
