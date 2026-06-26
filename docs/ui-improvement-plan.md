# Rencana Improvement UI/UX — Ruang Belajar

**Versi:** 1.0
**Tanggal:** 26 Juni 2026
**Konteks:** Penyelarasan UI custom (Orang Tua & Siswa) dengan [PRD v2](prd-v2.md), serta pemindahan seluruh fungsi administratif ke Django Admin.

---

## 1. Ringkasan & Prinsip

Dokumen ini adalah hasil audit UI yang ada saat ini (custom Django Templates + HTMX + Tailwind/Flowbite) dan rencana perbaikannya. Tiga keputusan besar:

1. **Custom UI hanya untuk 2 peran: Orang Tua & Siswa.** Sejalan dengan PRD v2 §8.1.
2. **Semua fungsi Admin & Pengajar pindah ke Django Admin.** Hilangkan custom UI admin (bank soal, tag, KD, blueprint, analytics sistem).
3. **UI custom direstrukturisasi mengikuti konsep data baru:** `Family` sebagai unit, `AcademicYear`/`Enrollment` (riwayat lintas tahun), dan jenjang SD+SMP (kelas 1–9), bukan lagi `grade` int 1–6.

Prinsip desain (turunan PRD §8.2): **mobile-first**, **minimal cognitive load**, **progressive disclosure**, **anak-friendly untuk siswa**, **data-rich tapi tidak cluttered untuk orang tua**.

---

## 2. Audit Kondisi Saat Ini

### 2.1 Pemetaan halaman custom yang ada

| Area | Template | Peran target sekarang | Keputusan |
|---|---|---|---|
| Router dashboard | `core/views.py::DashboardView` | semua | **Pertahankan** (admin sudah diarahkan ke `/admin/`) |
| Dashboard orang tua | `students/parent_dashboard.html` | Orang tua | **Redesign** |
| Daftar/kelola anak | `students/my_students.html`, `student_detail.html`, `create_student.html`, `link_student.html`, `link_requests.html`, `profile_edit.html` | Orang tua | **Pertahankan + rapikan** |
| Dashboard siswa | `students/dashboard.html` | Siswa | **Redesign** |
| Pengerjaan kuis | `quizzes/` (student-list, take_quiz, result, proxy) | Siswa / proxy ortu | **Pertahankan + polish** |
| Buat kuis | `quizzes/subject_quiz_create.html`, `custom_quiz_create.html` | Orang tua | **Pertahankan + sederhanakan** |
| Progress siswa | `analytics/progress.html` | Siswa | **Pertahankan + redesign** |
| **Bank soal CRUD** | `questions/` (list, form, detail, import, tag_*, kd_*) | Admin | **HAPUS → Django Admin** |
| **Kelola kuis (admin-style)** | `quizzes/list, form, detail, add_questions` | Admin | **HAPUS → Django Admin** |
| **Analytics sistem** | `analytics/admin_dashboard.html, tag_heatmap.html, kd_coverage.html` | Admin | **HAPUS → Django Admin** |
| Custom admin changelist | `templates/admin/questions/`, `templates/admin/quizzes/` | Admin | **Evaluasi** (lihat §5) |
| Deprecated | `students/list.html` (StudentListView, model Student lama) | — | **HAPUS** |

### 2.2 Temuan masalah UI/UX

**Konsistensi & branding**
- Branding tidak konsisten: title "Bank Soal SD" di navbar/template vs "Student Space" di README vs "Ruang Belajar" di PRD v2. **Samakan ke "Ruang Belajar".**
- Dua sistem navigasi paralel: `components/navbar.html` (top nav, pakai `is_pengajar_or_admin`) dan `components/sidebar.html` (pakai `is_admin`/`is_parent`). Aturan visibilitas tidak sinkron — parent bisa melihat menu admin di navbar tapi tidak di sidebar.

**Keterikatan ke model lama**
- Hard-coded "Kelas {{ user.grade }}" (int 1–6) di mana-mana → tidak kompatibel dengan jenjang SMP & konsep `Enrollment`/`AcademicYear`.
- Konsep `Family` belum tercermin di UI: dashboard orang tua memakai daftar `ParentStudent` link, belum ada gagasan "keluarga" / banyak anak dalam satu wadah, belum ada filter tahun ajaran.

**Dashboard orang tua (`parent_dashboard.html`)**
- Quick stats statis (3 kartu) tanpa sinyal aktionable PRD (F-18): "anak belum belajar N hari", "try-out tersedia".
- Tidak ada entry point ke fitur PRD v2: Try-out, Readiness Score, Study Plan, Riwayat Lintas Tahun, Laporan PDF, Subscription.
- Aktivitas terbaru hanya list flat, tanpa drill-down per anak.

**Dashboard siswa (`dashboard.html`)**
- Sudah cukup baik secara visual (hero, stats, performa mapel, aktivitas mingguan) tapi:
  - "Total XP" ditampilkan padahal gamification belum ada di data model (placeholder `total_xp`) → menyesatkan.
  - Bar chart aktivitas memakai trik inline `height: {{ count }}0%` yang rapuh.
  - Link "Lihat Detail" performa mapel `href="#"` (mati).
  - Memuat aset eksternal (`grainy-gradients.vercel.app`, noise.svg) → risiko privasi/offline, tidak sesuai "HTTPS wajib & self-contained".
- Belum ada: target ujian/countdown (F-16), study plan (F-17), badge/streak yang nyata.

**Aksesibilitas & teknis**
- Banyak ikon SVG inline berulang tanpa komponen → template gemuk, sulit dirawat.
- Beberapa elemen interaktif tanpa label aksesibilitas; kontras gradient hero perlu dicek WCAG AA (PRD §9.5).
- KaTeX/Chart.js dipakai tapi konsistensi loading belum dipastikan di semua halaman kuis.

---

## 3. Rencana Improvement — UI Orang Tua

### 3.1 Dashboard Orang Tua (redesign, F-18)

Struktur baru (mobile-first, progressive disclosure):

1. **Header keluarga + konteks tahun ajaran**
   - Nama keluarga, switcher **Tahun Ajaran** (default tahun aktif) — fondasi riwayat lintas tahun (F-20).
   - Badge status langganan (Free/Basic/Pro) + CTA upgrade halus (soft upsell, F-24/§7.4).
2. **Kartu per anak (bukan list flat)**
   - Avatar, nama, **enrollment saat ini** (jenjang + kelas + tahun ajaran), aktivitas terakhir, akurasi minggu ini.
   - Sinyal aktionable: "Belum belajar N hari", "Try-out tersedia", "Study plan diperbarui".
   - Aksi cepat: Lihat progress · Dampingi kuis · Mulai try-out.
3. **Ringkasan mingguan keluarga**
   - Total soal dikerjakan minggu ini, akurasi rata-rata, jumlah sesi — lintas semua anak.
4. **Panel notifikasi & rekomendasi**
   - Permintaan link tertunda, reminder, item study plan yang perlu didampingi.

Entry point fitur PRD v2 yang harus muncul (gated oleh plan): **Try-out**, **Readiness & Countdown**, **Study Plan**, **Riwayat Lintas Tahun**, **Laporan PDF**, **Kelola Langganan**.

### 3.2 Kelola Anak (rapikan)
- Pertahankan flow yang ada (tambah anak, link akun, verifikasi) — sudah solid.
- Ganti tampilan "Kelas N" → komponen **Enrollment** (jenjang + kelas + tahun ajaran) dengan tombol "Naik Kelas" (buat enrollment baru, F-03).
- Halaman detail anak (`parent_student_detail`) jadi pusat: tab Progress · Riwayat · Try-out · Study Plan · Laporan.

### 3.3 Buat/Konfigurasi Kuis (sederhanakan)
- Pertahankan `SubjectQuizCreateView` & `CustomQuizCreateView` sebagai UI orang tua (sesuai F-10 "orang tua/pengajar membuat konfigurasi quiz").
- Pindahkan **manajemen kuis administratif** (list global, edit, hapus, add/remove question satu per satu) ke Django Admin — orang tua cukup membuat & menjalankan, tidak mengelola katalog.
- Tambah pilihan **filter berbasis Tag** dan (nanti) sumber **QuestionSet**.

---

## 4. Rencana Improvement — UI Siswa

### 4.1 Dashboard Siswa (redesign ringan, F-18 siswa)
- **Hapus placeholder menyesatkan**: "Total XP" hanya ditampilkan jika gamification benar-benar diimplementasikan; sampai itu, ganti dengan metrik nyata (streak hari belajar dari data `Attempt`, atau "Akurasi minggu ini").
- **Self-host semua aset** (hapus dependensi `grainy-gradients.vercel.app`); gunakan gradient/pattern Tailwind lokal.
- **Perbaiki bar chart aktivitas**: gunakan tinggi terukur (kelas Tailwind / Chart.js), bukan `{{ count }}0%`.
- **Aktifkan link mati** ("Lihat Detail" performa → halaman progress per mapel).
- Konsep kelas mengikuti **Enrollment** (jenjang + kelas), bukan `user.grade`.

### 4.2 Pengerjaan Kuis & Try-out (polish, F-11/F-14)
- Pertahankan focus mode + HTMX partial navigation (sudah ada, auto-save via `views_ajax`).
- Pastikan: timer prominent (timed), tandai-ragu, navigasi maju/mundur, auto-submit, resume sesi (PRD F-11).
- Siapkan layout yang sama dipakai ulang untuk **Try-out berbasis blueprint** (per-seksi).
- Konsistenkan render KaTeX di soal & pembahasan.

### 4.3 Progress Siswa (redesign, F-19)
- Pindahkan dari satu halaman padat ke: ringkasan → akurasi per mapel → tren (Chart.js) → kekuatan/kelemahan per tag → cakupan KD.
- Tambah filter **tahun ajaran**.
- Anak-friendly: font besar, bahasa positif, visual sederhana.

### 4.4 Tambahan PRD v2 untuk siswa
- **Target ujian & countdown** (F-16), **Study plan** view read/check (F-17), **badge/streak** (future, hanya jika data model gamification ada).

---

## 5. Penghapusan UI Admin → Pindah ke Django Admin

Tujuan: hilangkan seluruh custom UI administratif. Semua dilayani Django Admin dengan kustomisasi `ModelAdmin` (list_display, list_filter, search_fields), inline, dan custom actions (PRD §6.7 / F-23).

### 5.1 Pemetaan rute custom → Django Admin

| Custom route (hapus) | Pengganti di Django Admin |
|---|---|
| `questions:list / create / detail / update / delete` | `QuestionAdmin` (filter kelas/mapel/topik/tag/kesulitan/tipe, bulk publish/archive) + `QuestionOption` inline |
| `questions:import` | Custom **admin action** / changelist button import JSON (F-08) |
| `questions:tag-*` (CRUD) | `TagAdmin` |
| `questions:kd-*` (CRUD) | `KompetensiDasar`/`CompetencyAdmin` |
| `quizzes:list / create / detail / update / delete / question-add / question-remove` | `QuizAdmin` + `Question` inline/filter_horizontal |
| `analytics:dashboard` | Django Admin index / `django-admin-charts` (opsional) |
| `analytics:tag-heatmap`, `kd-coverage`, `student-history` | Admin changelist + readonly views / export actions |
| `analytics:export-student`, `export-class` | Admin actions "Export report" |
| `students:list` (StudentListView, model lama) | **Hapus total** (model `Student` deprecated) |

### 5.2 Yang TETAP custom (orang tua/siswa)
- `quizzes:student-list`, `take_quiz`, `save_answer`, `result`, `proxy_select`
- `quizzes:create_subject_quiz`, `create_custom_quiz` (konfigurasi kuis oleh ortu)
- `analytics:progress` (progress siswa)
- Semua rute `students:*` non-deprecated (kelola anak, link, verifikasi)

### 5.3 Pembersihan navigasi
- **Navbar (`components/navbar.html`)**: hapus link admin (Bank Soal, Tags, KD, Analytics). Untuk admin/superuser cukup tautan tunggal **"Admin Panel" → `/admin/`**.
- **Sidebar (`components/sidebar.html`)**: hapus seluruh blok `{% if user.is_admin %}` (Materi & Soal, Aktivitas). Sidebar hanya melayani Orang Tua & Siswa.
- Samakan aturan visibilitas: berhenti memakai `is_pengajar_or_admin` di UI custom; admin tidak punya UI custom sama sekali.

### 5.4 Django Admin kustomisasi (sesuai F-23)
- `ModelAdmin` informatif: `list_display`, `list_filter`, `search_fields` untuk semua model referensi & konten.
- Inline: `QuestionOption` di `Question`, `ExamSection` di `ExamBlueprint`, `PlanFeature` di `Plan`.
- Custom actions: import JSON, bulk publish/archive, export laporan.
- Readonly fields untuk data terhitung (skor, transaksi pembayaran).
- Permission groups: *content manager*, *user manager*, *finance* (F-23).
- Pengajar dilayani **Django Admin terbatas** via permission group (bukan custom UI).

---

## 6. Komponen & Fondasi Teknis UI

- **Konsolidasi komponen**: ekstrak ikon SVG berulang ke `templates/components/icons/` atau template tag; perluas `components/` (stat_card, student_card, section_header, year_switcher, plan_badge).
- **Layout**: satu `base_dashboard` dengan sidebar peran-aware (hanya ortu/siswa). Tambah `base_public` untuk landing/pricing (Phase 6).
- **Branding**: ganti seluruh "Bank Soal SD" → **"Ruang Belajar"**.
- **Aset**: self-host semua (hapus CDN pihak ketiga non-esensial); pastikan KaTeX, Chart.js, HTMX, Flowbite konsisten.
- **Aksesibilitas (PRD §9.5)**: semantic HTML, label ARIA, kontras WCAG AA, keyboard-navigable, font adjustable di siswa view.
- **HTMX**: standarkan partial untuk navigasi soal, lazy-load chart, inline edit profil, toggle enrollment.

---

## 7. Eksekusi Bertahap (selaras Roadmap PRD)

> Catatan: beberapa item bergantung pada refactor data model (Family, AcademicYear, Enrollment, Grade FK). Lihat juga rencana migrasi fondasi akademik.

| Tahap | Pekerjaan UI | Bergantung pada |
|---|---|---|
| **U0 — Bersih-bersih** | Hapus custom UI admin (§5), bersihkan navbar/sidebar, hapus `students/list.html` deprecated, samakan branding | — |
| **U1 — Django Admin** | Kustomisasi `ModelAdmin`, inline, actions, permission groups (§5.4) | — |
| **U2 — Fondasi ortu/siswa** | Ganti `user.grade` → Enrollment di UI; year switcher; konsep Family di dashboard | Model: Family, AcademicYear, Enrollment, Grade |
| **U3 — Dashboard redesign** | Redesign dashboard ortu (F-18) & siswa; perbaiki bug chart/link/aset | U2 |
| **U4 — Fitur PRD v2** | UI Try-out, Readiness/Countdown, Study Plan, Riwayat lintas tahun, Laporan PDF | Modul tryouts & analytics lanjutan |
| **U5 — Monetisasi** | Plan badge, gating halus, pricing & landing page | Modul subscriptions |

---

## 8. Definition of Done (DoD) untuk fase UI awal (U0–U1)

- Tidak ada lagi rute/template custom untuk admin; akses admin sepenuhnya via `/admin/`.
- Navbar & sidebar hanya menampilkan menu yang relevan untuk Orang Tua & Siswa.
- Model `Student` lama & template terkait dihapus.
- Branding seragam "Ruang Belajar".
- Django Admin: question bank, tag, KD, kuis, subjek/topik bisa dikelola penuh dengan filter/search/inline/actions.
- Tidak ada dependensi aset eksternal non-esensial; tidak ada link/elemen mati di dashboard.
