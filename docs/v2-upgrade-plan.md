# Rencana Upgrade Aplikasi menuju v2

**Versi:** 1.0
**Tanggal:** 26 Juni 2026
**Acuan:** [PRD v2](prd-v2.md) · berpasangan dengan [UI Improvement Plan](ui-improvement-plan.md)

Dokumen ini memetakan **apa yang perlu dibuat / diubah** di backend & data model untuk mencapai PRD v2, dengan prinsip **evolusi non-destruktif**: tambahkan yang belum ada, ubah seperlunya dengan migrasi bertahap, dan pastikan tidak merusak fitur yang sudah jalan. Bagian akhir (§6) mengkonsolidasikan urutan kerja backend (B) dengan urutan UI (U).

---

## 1. Prinsip & Strategi Kompatibilitas

1. **Lanjutkan, bukan rewrite.** Stack, auth, quiz engine, Attempt tracking, dan pipeline deploy dipertahankan (lihat penilaian arsitektur di PRD §1.3 & §4).
2. **Expand → migrate → contract.** Setiap perubahan breaking dilakukan dalam 3 langkah migrasi agar zero-downtime & reversible:
   - *Expand:* tambah kolom/tabel baru (nullable), tanpa menyentuh yang lama.
   - *Migrate:* data migration mengisi struktur baru dari data lama; kode mulai membaca yang baru (dengan fallback).
   - *Contract:* setelah stabil, hapus kolom/tabel lama.
3. **Additive dulu.** Modul yang sepenuhnya baru (`academic`, `tryouts`, `subscriptions`, analytics lanjutan) tidak menyentuh tabel lama → low risk, kerjakan paralel.
4. **Tiap migrasi punya test.** Jalankan `pytest` + E2E (`tests/e2e/`) sebelum & sesudah tiap fase. DoD fase = test hijau + fitur lama tidak regresi.
5. **Seed & data migration disertakan**, bukan manual, agar reproducible di dev/staging/prod.

---

## 2. Gap Analysis: Kondisi Sekarang → Target v2

Legenda dampak: 🟢 additive (aman) · 🟡 ubah dengan migrasi data · 🔴 refactor breaking (perlu expand-contract).

### 2.1 Accounts & Family

| Entitas v2 | Status sekarang | Aksi | Dampak |
|---|---|---|---|
| `User` (role) | Ada (admin/parent/student) | Tambah role `tutor` | 🟢 |
| `Family` | **Belum ada** | Buat; jadi root tenancy & basis Subscription | 🟡 |
| `StudentProfile` | Student = `User(role=student)` + fields | **Keputusan desain** (lihat §3.1): pertahankan User-based, jangan pecah ke tabel baru | 🟡 |
| `ParentProfile` | **Belum ada** (preferensi tersebar) | Buat (notifikasi/settings), `OneToOne(User)` | 🟢 |
| `TutorProfile` | **Belum ada** | Buat | 🟢 |
| `ParentStudent` link | Ada (workflow verifikasi) | Pertahankan; tautkan ke `Family` | 🟡 |

### 2.2 Academic Reference (app baru `academic`)

| Entitas v2 | Status sekarang | Aksi | Dampak |
|---|---|---|---|
| `EducationLevel` (SD/SMP) | **Belum ada** | Buat | 🟢 |
| `Grade` (kelas 1–9) | `grade` = **IntegerField 1–6** di banyak model | Buat tabel `Grade`; ganti semua `grade:int` → `FK(Grade)` | 🔴 |
| `Subject` | Ada di app `subjects`, punya `grade:int` | Pindah konsep ke `academic`; lepas dari `grade` langsung | 🔴 |
| `GradeSubject` | **Belum ada** (mapel nempel ke grade via int) | Buat M2M Grade×Subject | 🟡 |
| `Topic` | Ada (`subjects.Topic`, FK Subject) | Selaraskan ke `GradeSubject` | 🟡 |
| `Competency` (KD) | `questions.KompetensiDasar`, FK **Subject** + `grade:int` | Pindah relasi KD → **Topic**; ganti grade int | 🟡 |
| `AcademicYear` | **Belum ada** | Buat | 🟢 |
| `Enrollment` | **Belum ada** (kelas anak = `User.grade`) | Buat (Student×Grade×AcademicYear); jadi sumber "kelas saat ini" & riwayat | 🟡 |

### 2.3 Questions & Content

| Entitas v2 | Status sekarang | Aksi | Dampak |
|---|---|---|---|
| `Question` | Ada (FK Topic) | Tambah field `status` (draft/published/archived), tipe `benar/salah`, `source` | 🟢 |
| `QuestionOption` | Opsi = **JSONField** di Question | **Opsional** — JSON sudah cukup; pecah ke tabel hanya bila perlu query per-opsi | 🟢 |
| `Tag` | Ada | Pertahankan | 🟢 |
| `QuestionSet` | **Belum ada** | Buat (M2M kurasi soal) | 🟢 |
| `ImportBatch` | Import ada, tanpa metadata batch | Buat (audit trail + rollback) | 🟢 |

### 2.4 Quizzes

| Entitas v2 | Status sekarang | Aksi | Dampak |
|---|---|---|---|
| `QuizConfig` | `quizzes.Quiz` sudah berperan sbg config | Selaraskan field (mode practice/timed/custom, filter tag) — **tidak perlu model baru** | 🟡 |
| `QuizSession` | Ada (lengkap, + proxy mode) | Tambah status (in_progress/completed/timed_out/abandoned), skor per tag | 🟢 |
| `QuizAnswer` | = `analytics.Attempt` | **Pertahankan Attempt** (rename opsional); sudah menyimpan jawaban, benar/salah, waktu, urutan | 🟢 |

### 2.5 Try-out & TKA (app baru `tryouts`) — semua 🟢 additive

`ExamBlueprint`, `ExamSection`, `TryoutSession`, `TryoutSectionScore`, `StudyPlan`, `StudyPlanItem`, `ExamTarget`. Tidak menyentuh tabel lama; konsumsi `Question`/`Tag`/`Topic` yang sudah ada.

### 2.6 Analytics

| Entitas v2 | Status sekarang | Aksi | Dampak |
|---|---|---|---|
| `Attempt` | Ada | Pertahankan (sumber kebenaran jawaban) | 🟢 |
| `ProgressSnapshot` | **Belum ada** | Buat + Celery job periodik | 🟢 |
| `MasteryRecord` | **Belum ada** | Buat; update saat quiz/try-out selesai | 🟢 |

### 2.7 Subscriptions (app baru `subscriptions`) — semua 🟢 additive

`Plan`, `PlanFeature`, `Subscription`, `Invoice`, `PaymentTransaction` + middleware feature gating. Tidak ada selama belum diaktifkan → tidak merusak apa pun.

### 2.8 Deprecated yang aman dihapus

- `apps/students` model `Student` (lama) — **tidak ada FK aktif** yang menunjuk ke sana (quizzes/analytics sudah pakai `User`). Aman dihapus setelah memastikan tak ada data produksi yang bergantung. 🟡

---

## 3. Keputusan Desain Penting (perlu dikonfirmasi sebelum eksekusi)

### 3.1 StudentProfile: tabel baru (PRD) vs User-based (sekarang)
PRD menggambarkan `StudentProfile` terpisah dari `User`. Codebase sekarang memakai `User(role=student)` + `ParentStudent`, dan **semua FK** (`QuizSession.student`, `Attempt.student`) menunjuk ke `User`.
**Rekomendasi:** **pertahankan model User-based.** Memecah ke `StudentProfile` berarti memigrasi semua FK = risiko tinggi tanpa manfaat sepadan. Petakan konsep PRD ke realita: "StudentProfile" = `User(role=student)` + (opsional) `ParentProfile`-style thin profile. `Family` cukup menambah satu FK pengelompokan.

### 3.2 `grade` integer → `Grade` FK (refactor 🔴 terbesar)
Muncul di `User`, `subjects.Subject`, `questions.KompetensiDasar`, `quizzes.Quiz`, `quizzes.QuizSession`. Pakai expand-contract:
1. Tambah `grade_ref = FK(Grade, null=True)` di tiap model (expand).
2. Seed `EducationLevel`+`Grade` (SD 1–6, SMP 7–9); data migration isi `grade_ref` dari `grade:int`.
3. Pindahkan kode baca/tulis ke `grade_ref`; "kelas anak" dibaca dari `Enrollment` aktif, bukan `User.grade`.
4. Setelah stabil: hapus `grade:int` & `MaxValueValidator(6)` (contract).

### 3.3 KD → Topic
`KompetensiDasar` saat ini FK ke `Subject`. PRD ingin KD melekat ke `Topic`. Expand: tambah `topic = FK(Topic, null=True)`, backfill bila memungkinkan (atau biarkan admin reassign), lalu jadikan sumber utama.

### 3.4 QuestionOption
Tetap **JSONField** kecuali ada kebutuhan nyata. Jika dipecah, lakukan additive (buat tabel, sync dari JSON, baru pindah render).

---

## 4. Rencana per-Fase Backend (B)

> Tiap fase = migrasi (expand/migrate/contract sesuai kebutuhan) + admin kustomisasi + test. Lihat juga peta Django Admin di UI plan §5.

| Fase | Lingkup | Output | Risiko |
|---|---|---|---|
| **B0 — Prep** | Setup Celery+Redis (opsional/feature-flag), struktur seed, baseline test snapshot | Fondasi tooling tanpa ubah skema | 🟢 |
| **B1 — Academic foundation** | App `academic`: EducationLevel, Grade, AcademicYear, GradeSubject; refactor `grade:int`→FK; Subject pindah/relasi; KD→Topic; Enrollment | Jenjang SD+SMP, riwayat tahun ajaran | 🔴 |
| **B2 — Family & roles** | `Family`, `ParentProfile`, `TutorProfile`, role `tutor`; tautkan ParentStudent→Family | Unit keluarga sbg tenancy | 🟡 |
| **B3 — Questions+** | `status`, tipe benar/salah, `QuestionSet`, `ImportBatch` (audit+rollback) | Content pipeline matang | 🟢 |
| **B4 — Quizzes align** | Selaraskan Quiz→QuizConfig (mode, filter tag), status QuizSession | Quiz engine sesuai PRD F-10..F-12 | 🟡 |
| **B5 — Tryouts** | App `tryouts` lengkap (blueprint→session→score→study plan→target) | Fitur TKA F-13..F-17 | 🟢 |
| **B6 — Analytics adv** | `ProgressSnapshot`, `MasteryRecord`, Celery batch jobs | Dashboard data-driven F-19..F-22 | 🟢 |
| **B7 — Subscriptions** | App `subscriptions` + middleware feature gating + webhook payment | Monetisasi F-? / §7 | 🟢 |
| **B8 — Cleanup** | Hapus model `Student` lama, `grade:int`, shim deprecated | Codebase bersih | 🟡 |

---

## 5. Checklist Non-Breaking (per fase)

- [ ] Migrasi reversible (punya `reverse_code` atau aman di-rollback).
- [ ] `pytest` + `tests/e2e/` hijau sebelum & sesudah.
- [ ] Fitur lama yang relevan diuji manual (login, buat kuis, kerjakan kuis, lihat progress).
- [ ] Tidak ada FK menggantung; data lama ter-backfill.
- [ ] `makemigrations --check` bersih; `migrate` sukses di DB kosong **dan** DB ber-data.
- [ ] Seed/data migration idempotent.
- [ ] Django Admin tetap bisa CRUD entitas terdampak.

---

## 6. Master Sequence (Konsolidasi Backend B + UI U)

Mengurutkan fase backend (dokumen ini) dan fase UI ([UI plan §7](ui-improvement-plan.md#7-eksekusi-bertahap-selaras-roadmap-prd)) ke dalam satu jalur kerja, dengan ketergantungan eksplisit.

| # | Langkah | Sumber | Bergantung pada | Catatan |
|---|---|---|---|---|
| 1 | **B0** Prep tooling & baseline test | B0 | — | Aman, paralel |
| 2 | **U0** Hapus custom UI admin + bersihkan nav | U0 | — | Tidak butuh model baru → kerjakan lebih awal |
| 3 | **U1** Django Admin kustomisasi (ModelAdmin/inline/actions/groups) | U1 | U0 | Jadikan admin fungsional sebelum refactor |
| 4 | **B1** Academic foundation (grade→FK, AcademicYear, Enrollment, KD→Topic) | B1 | B0 | Refactor 🔴 terbesar; expand-contract |
| 5 | **B2** Family, ParentProfile, TutorProfile, role tutor | B2 | B1 | Tenancy root |
| 6 | **U2** UI ortu/siswa pakai Enrollment + Family + year switcher | U2 | B1, B2 | UI berhenti pakai `user.grade` |
| 7 | **B3** Questions+ (status, set, import batch) · **B4** Quizzes align | B3, B4 | B1 | Bisa paralel |
| 8 | **U3** Redesign dashboard ortu & siswa; perbaiki bug aset/chart/link | U3 | U2 | |
| 9 | **B5** Tryouts · **B6** Analytics lanjutan (+Celery) | B5, B6 | B1, B4 | Additive, bisa paralel |
| 10 | **U4** UI Try-out, Readiness/Countdown, Study Plan, Riwayat, Laporan PDF | U4 | B5, B6 | |
| 11 | **B7** Subscriptions + feature gating | B7 | B2 | |
| 12 | **U5** Plan badge, gating halus, pricing & landing page | U5 | B7 | |
| 13 | **B8** Cleanup (hapus Student lama, grade:int, shim) | B8 | semua di atas | Contract terakhir |

**Jalur kritis:** B0 → B1 → B2 → (B3/B4) → (B5/B6) → B7 → B8.
**UI mengikuti:** U0/U1 dapat berjalan sangat awal (independen); U2+ menunggu fondasi data (B1/B2); U4 menunggu B5/B6; U5 menunggu B7.

Pemetaan ke Roadmap PRD §10: U0–U1+B0 ≈ pra-Phase 1 · B1–B2+U2 ≈ Phase 1 · B3–B4+U3 ≈ Phase 2 · B5+U4 ≈ Phase 3 · B6 ≈ Phase 4 · B7+U5 ≈ Phase 5 · B8+landing ≈ Phase 6.

---

## 7. Rekomendasi Titik Mulai

Mulai dari **langkah 2–3 (U0+U1)**: menghapus custom UI admin dan mengandalkan Django Admin. Ini **tanpa risiko skema**, langsung menyederhanakan codebase, dan menyiapkan admin yang fungsional sebelum masuk refactor 🔴 di **B1**. Setelah itu B1 (academic foundation) adalah fondasi yang membuka hampir semua fitur v2.
